from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from uuid import uuid4
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from .models import Order
from django.urls import reverse
from .models import OrderItem, Product, Comment, Category, UserProfile, Order, DeliveryContact
from .forms import CommentForm, SignUpForm, UserProfileForm, OrderForm, DeliveryContactForm
from .mpesa import initiate_payment
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .cart import CartClass
from .models import Product
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import SignUpForm
from .utils import send_verification_email  # Assuming `send_verification_email` is in utils.py or adjust import accordingly
# Utility function to send verification email
from django.http import JsonResponse
def send_verification_email(user):
    code = str(uuid4())
    try:
        profile = UserProfile.objects.get(user=user)
        profile.email_verification_code = code
        profile.save()
    except UserProfile.DoesNotExist:
        messages.error(request, 'UserProfile not found for the newly registered user.')
        return
    verification_link = f"http://localhost:8000/verify-email/{code}/"  # Update to your live site URL
    send_mail(
        'Verify Your Email Address',
        f'Click the link to verify your email: {verification_link}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

# Email verification view
def verify_email(request, code):
    try:
        profile = UserProfile.objects.get(email_verification_code=code)
        profile.email_verified = True
        profile.email_verification_code = ''
        profile.save()
        messages.success(request, 'Email successfully verified.')
        return redirect('login')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid verification code.')
        return redirect('signup')

# View for the index page
def index(request):
    featured_products = Product.objects.filter(is_featured=True).select_related('category')[:8]
    categories = Category.objects.all()

    # Instantiate the cart with the request
    cart = CartClass(request)
    cart_count = len(cart) if request.user.is_authenticated else 0

    return render(request, 'shop/index.html', {
        'featured_products': featured_products,
        'categories': categories,
        'cart_count': cart_count
    })


# View for product details, includes form for adding comments and ratings
@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = product.related_products.all().exclude(id=product_id).select_related('category')
    comments = product.comments.all().order_by('-created_at')

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                existing_comment = Comment.objects.filter(product=product, user=request.user).first()
                if existing_comment:
                    messages.warning(request, "You have already commented on this product.")
                else:
                    comment = form.save(commit=False)
                    comment.user = request.user
                    comment.product = product
                    comment.save()
                    if request.is_ajax():
                        comments = product.comments.all().order_by('-created_at')
                        comments_html = render_to_string('shop/comments_list.html', {'comments': comments})
                        return JsonResponse({'success': True, 'comments_html': comments_html})
                    messages.success(request, "Your comment has been added.")
                return redirect('product_detail', product_id=product.id)
        elif 'rate_product' in request.POST:
            rating = request.POST.get('rating')
            if rating:
                try:
                    rating = Decimal(rating)
                    Comment.objects.update_or_create(
                        user=request.user,
                        product=product,
                        defaults={'rating': rating, 'text': 'Rating only'}
                    )
                    if request.is_ajax():
                        return JsonResponse({'success': True})
                except (ValueError, Decimal.InvalidOperation):
                    return JsonResponse({'success': False, 'error': 'Invalid rating'})
    
    else:
        form = CommentForm()

    recommended_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'comments': comments,
        'form': form,
        'recommended_products': recommended_products
    })

# View for adding a comment to a product
@login_required
def add_comment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if Comment.objects.filter(user=request.user, product=product).exists():
        messages.error(request, 'You have already commented on this product.')
        return redirect('product_detail', product_id=product.id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.save()
            messages.success(request, 'Your comment has been added.')

            if request.is_ajax():
                comments = product.comments.all().order_by('-created_at')
                comments_html = render_to_string('shop/comments_list.html', {'comments': comments})
                return JsonResponse({'success': True, 'comments_html': comments_html})

            return redirect('product_detail', product_id=product.id)
    else:
        form = CommentForm()

    return redirect('product_detail', product_id=product.id)

# View for rating a product
@login_required
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    rating = request.POST.get('rating')
    
    if rating:
        try:
            rating = Decimal(rating)
            Comment.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={'rating': rating, 'text': 'Rating only'}
            )
            return JsonResponse({'success': True})
        except (ValueError, Decimal.InvalidOperation):
            return JsonResponse({'success': False, 'error': 'Invalid rating'})
    
    return JsonResponse({'success': False, 'error': 'No rating provided'})

# View for listing products with search and filtering options
def product_list(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', '')
    
    filters = Q()
    
    if query:
        filters &= Q(name__icontains=query) | Q(description__icontains=query)
        
    if category_id:
        filters &= Q(category_id=category_id)
    
    products = Product.objects.filter(filters).select_related('category')
    paginator = Paginator(products, 10)  # 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'shop/products_partial.html', {'products': page_obj})
    
    categories = Category.objects.all()
    return render(request, 'shop/products.html', {
        'products': page_obj,
        'categories': categories
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Fetch product by UUID
    cart = CartClass(request)  # Use the cart instance linked to the session
    cart.add(product)  # Add product to the cart
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('view_cart')

@login_required

def view_cart(request):
    cart = CartClass(request)
    return render(request, 'shop/cart.html', {
        'cart': cart,
        'total_price': cart.get_total_price(),
        'item_count': len(cart)  # Add this line to pass the count to the template
    })

@login_required
def update_cart_item(request, product_id):
    cart = CartClass(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart.add(product, quantity=quantity, update_quantity=True)
        messages.success(request, f"Updated {product.name} quantity to {quantity}.")
    else:
        messages.error(request, "Quantity must be greater than zero.")
    return redirect('view_cart')

@login_required
def remove_from_cart(request, product_id):
    cart = CartClass(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f"{product.name} has been removed from your cart.")
    return redirect('view_cart')




from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Order, OrderItem
from .cart import CartClass  # Assuming CartClass is defined properly
@login_required
def checkout(request):
    cart = CartClass(request)

    if request.method == 'POST' and cart.get_total_price() > 0:
        try:
            # Create an order from the cart
            order = Order.objects.create(
                user=request.user,
                total_price=cart.get_total_price(),
                # Include other fields like address, payment status, etc., as needed
            )

            # Loop through cart items and create OrderItem entries for each
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price'],
                )

            # Clear the cart after creating the order
            cart.clear()

            # Send confirmation message to user
            messages.success(request, "Your order has been placed successfully!")

            # Send order confirmation email to user
            user_email_subject = "Order Confirmation"
            user_email_message = render_to_string('shop/order_confirmation_email.html', {
                'order': order,
                'user': request.user
            })
            send_mail(user_email_subject, user_email_message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

            # Send notification email to admin
            admin_email_subject = f"New Order Received: #{order.id}"
            admin_email_message = render_to_string('shop/admin_order_notification_email.html', {
                'order': order,
                'user': request.user
            })
            send_mail(admin_email_subject, admin_email_message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])

            # Redirect to order_detail view with the correct UUID order_id
            return redirect('order_detail', order_id=order.id)

        except Exception as e:
            # Handle any error during order creation, email sending, etc.
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('cart')  # Or any fallback view to retry

    # Render checkout page if cart is empty or order creation fails
    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'total_price': cart.get_total_price()
    })



# View for purchasing a product
@login_required
def purchase(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        delivery_contact_form = DeliveryContactForm(request.POST)
        
        if form.is_valid() and delivery_contact_form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'Pending'
            order.save()
            
            contact = delivery_contact_form.save(commit=False)
            contact.order = order
            contact.save()
            
            if 'payment_method' in request.POST and request.POST['payment_method'] == 'mpesa':
                amount = order.total_price
                response = initiate_payment(request.user, amount)
                if response['success']:
                    return redirect(response['payment_url'])
                else:
                    messages.error(request, 'Payment initiation failed.')
                    return redirect('checkout')
            else:
                # Handle Cash on Delivery
                messages.success(request, 'Order placed successfully. We will contact you soon.')
                return redirect('order_status', order_id=order.id)
    
    else:
        form = OrderForm()
        delivery_contact_form = DeliveryContactForm()
    
    return render(request, 'shop/checkout.html', {
        'form': form,
        'delivery_contact_form': delivery_contact_form
    })

# View for tracking order status
@login_required
def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_status.html', {
        'order': order
    })

# View for managing delivery contacts
@login_required
def manage_delivery_contacts(request):
    if request.method == 'POST':
        form = DeliveryContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, 'Delivery contact added successfully.')
            return redirect('manage_delivery_contacts')
    else:
        form = DeliveryContactForm()

    contacts = DeliveryContact.objects.filter(user=request.user)
    return render(request, 'shop/manage_delivery_contacts.html', {
        'form': form,
        'contacts': contacts
    })
    
# views.py


def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order_detail.html', {'order': order})

# views.py

# User signup view with email verification logic

from django.contrib import messages
from .utils import send_verification_email
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)  # Save user instance without committing to the database yet
            user.is_active = False  # Deactivate account until email verification is complete
            user.save()  # Now save it to the database
            
            send_verification_email(request, user)  # Send email verification link
            
            messages.success(request, 'Account created successfully. Please check your email to verify your account.')
            return redirect('login')  # Redirect to login after signup

        # If the form is invalid, display an error message
        else:
            messages.error(request, 'There was an error with your signup. Please check the form fields below.')

    else:
        form = SignUpForm()  # If GET request, initialize an empty form

    return render(request, 'registration/signup.html', {'form': form})

#This view will handle the verification link from the email, activating the user if the token is valid.


User = get_user_model()

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate the user
        user.save()
        messages.success(request, 'Your account has been verified successfully! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
        return render(request, 'registration/activation_failed.html')



# views.py
# User authentication views
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})



# shop/views.py


def custom_logout_view(request):
    logout(request)
    # Store the current page in the session to redirect back after logout
    next_page = request.META.get('HTTP_REFERER', '/')  # Fallback to '/' if no referrer
    messages.success(request, "You have successfully logged out.")
    return redirect(next_page)
  



from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import UserProfile

@login_required
def profile(request):
    # Check if the user has a UserProfile and create one if it doesn’t exist
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)

    # Now it's safe to access userprofile
    if not request.user.userprofile.email_verified:
        messages.warning(request, 'Please verify your email to access this page.')
        return redirect('login')

    profile = request.user.userprofile
    return render(request, 'shop/profile.html', {'profile': profile})


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import UserProfileForm
from .models import UserProfile

@login_required
def update_profile(request):
    # Ensure the user has a UserProfile; create it if not.
    user = request.user
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user.userprofile)
    
    return render(request, 'shop/update_profile.html', {'form': form})



def mpesa_callback(request):
    if request.method == 'POST':
        # Process the Mpesa callback data
        callback_data = request.body
        # Do something with the callback_data (e.g., validate, update order status)
        
        # Return a response to acknowledge the callback
        return JsonResponse({"status": "Success", "message": "Mpesa callback received."})
    else:
        return JsonResponse({"status": "Failed", "message": "Invalid request method."})

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from .models import UserProfile

def verify_email(request, code):
    try:
        # Try to find the profile with the verification code
        profile = UserProfile.objects.get(email_verification_code=code)

        # Activate the user
        user = profile.user
        user.is_active = True
        user.save()

        # Clear the verification code as it's already used
        profile.email_verification_code = ""
        profile.save()

        # Redirect to the login page with a success message
        messages.success(request, "Your email has been verified successfully. You can now log in.")
        return redirect('login')  # Assuming your login URL is named 'login'

    except UserProfile.DoesNotExist:
        # If the verification code is invalid or not found
        raise Http404("Invalid verification code")


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from uuid import uuid4

def send_verification_email(user):
    code = str(uuid4())
    try:
        profile = UserProfile.objects.get(user=user)
        profile.email_verification_code = code
        profile.save()

        # Email content
        subject = "Verify your email address"
        html_message = render_to_string('your_app/email_verification.html', {
            'user': user,
            'verification_code': code,
        })
        plain_message = strip_tags(html_message)  # Generate plain-text version for non-HTML email clients

        # Create the email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,  # Plain text content
            from_email='mikemwazo444@gmail.com',
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")  # Add HTML content as an alternative
        email.send()

    except UserProfile.DoesNotExist:
        # Log or handle error
        print("UserProfile not found for the newly registered user.")



# Additional utility views
def contact(request):
    return render(request, 'shop/contact.html')

def privacy_policy(request):
    return render(request, 'shop/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'shop/terms_of_service.html')

def faqs(request):
    return render(request, 'shop/faqs.html')

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Logic to handle newsletter subscription
        messages.success(request, 'Subscribed to newsletter successfully!')
    return redirect('index')

def about(request):
    return render(request, 'shop/about.html')
