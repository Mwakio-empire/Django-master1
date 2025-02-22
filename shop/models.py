import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Function to validate phone number
def validate_phone_number(value):
    if not value.isdigit() or len(value) < 10 or len(value) > 15:
        raise ValidationError("Enter a valid phone number with 10 to 15 digits.")

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = models.ImageField(upload_to='product_images/', default='product_images/default_image.jpg')
    additional_images = models.ManyToManyField('ProductImage', blank=True, related_name='products_with_additional_images')
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    related_products = models.ManyToManyField('self', blank=True, symmetrical=False)
    comments = models.ManyToManyField('Comment', blank=True, related_name='commented_products')
    
    # Seller contact details for delivery
    contact_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def featured_products(cls):
        return cls.objects.filter(is_featured=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase of {self.product.name} by {self.user.username}"

class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField()

    def __str__(self):
        return f"Recommendation of {self.product.name} by {self.user.username} with score {self.score}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email_verification_code = models.UUIDField(default=uuid.uuid4, editable=False)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.user.username}"

# Add a DeliveryContact model
class DeliveryContact(models.Model):
    username = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15, validators=[validate_phone_number])
    available = models.BooleanField(default=True)  # To show if this contact is available for delivery

    def __str__(self):
        return f"{self.username} - {self.phone_number}"

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('cod', 'Cash on Delivery'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_state = models.CharField(max_length=100, blank=True, null=True)
    shipping_zip = models.CharField(max_length=20, blank=True, null=True)
    shipping_country = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ], default='unpaid')
    delivery_contact = models.ForeignKey(DeliveryContact, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    mpesa_code = models.CharField(max_length=50, blank=True, null=True)  # For M-Pesa payments
    tracking_number = models.CharField(max_length=50, blank=True, null=True)  # Optional tracking number

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_total(self):
        return sum(item.get_total() for item in self.order_items.all())

    def __str__(self):
        return f"Order {self.order_number} for {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"



