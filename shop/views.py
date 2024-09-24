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

from .models import Product, Cart, Comment, Category, UserProfile, Order, DeliveryContact
from .forms import CommentForm, SignUpForm, UserProfileForm, OrderForm, DeliveryContactForm
from .mpesa import initiate_payment

# Utility function to send verification email
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
    cart_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
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

# View for adding a product to the cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart.quantity += 1
        cart.save()
    return redirect('view_cart')

# View for displaying the cart items
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.get_total() for item in cart_items)

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price
    })

# View for removing a product from the cart
@login_required
def remove_from_cart(request, product_id):
    Cart.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('view_cart')

# View for updating the quantity of a product in the cart
@login_required
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    quantity = request.POST.get('quantity')
    
    if quantity:
        try:
            quantity = int(quantity)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully.')
            else:
                messages.error(request, 'Quantity must be greater than zero.')
        except ValueError:
            messages.error(request, 'Invalid quantity.')
    
    return redirect('view_cart')

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

from django.shortcuts import render, get_object_or_404
from .models import Order

def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order_detail.html', {'order': order})

# views.py

# User signup view with email verification logic
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_verification_email(user)
            messages.success(request, 'Account created successfully. Please verify your email.')
            return redirect('index')
    else:
        form = SignUpForm()
    
    return render(request, 'shop/signup.html', {'form': form})


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
    return render(request, 'shop/login.html', {'form': form})



# shop/views.py


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile(request):
    if not request.user.userprofile.email_verified:
        messages.warning(request, 'Please verify your email to access this page.')
        return redirect('signup')

    profile = request.user.userprofile
    return render(request, 'shop/profile.html', {'profile': profile})

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'shop/update_profile.html', {'form': form})

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
