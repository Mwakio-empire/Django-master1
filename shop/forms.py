from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Comment, UserProfile, Cart
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'}),
        }

    def clean_rating(self):
        """Validate that the rating is between 1 and 5."""
        rating = self.cleaned_data.get('rating')
        if rating is None or not (1 <= rating <= 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Create a password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        }

    def clean_email(self):
        """Ensure the email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        """Save the user instance with the email address."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
        }

    def clean_phone_number(self):
        """Validate that the phone number contains only digits."""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        return phone_number

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')
        widgets = {
            'old_password': forms.PasswordInput(attrs={'placeholder': 'Old Password'}),
            'new_password1': forms.PasswordInput(attrs={'placeholder': 'New Password'}),
            'new_password2': forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
        }

    def clean_old_password(self):
        """Validate the old password is correct."""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("Old password is incorrect.")
        return old_password

    def clean_new_password1(self):
        """Validate the new password with Django's built-in validators."""
        new_password = self.cleaned_data.get('new_password1')
        validate_password(new_password)  # Enforce strong password policies
        return new_password

    def clean_new_password2(self):
        """Ensure the new passwords match."""
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 != new_password2:
            raise ValidationError("New passwords do not match.")
        return new_password2

class CartUpdateForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Quantity'}),
        }

    def clean_quantity(self):
        """Ensure the quantity is a positive integer."""
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive integer.")
        return quantity

# forms.py

from django import forms
from .models import Order, DeliveryContact

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_zip', 'shipping_country', 'payment_method'
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 2}),
            'payment_method': forms.Select(choices=[('cash', 'Cash'), ('mpesa', 'M-Pesa')]),
        }


# forms.py

from django import forms
from .models import DeliveryContact

class DeliveryContactForm(forms.ModelForm):
    class Meta:
        model = DeliveryContact
        fields = ['username', 'phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={'type': 'tel'}),
        }

# shop/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    # You can customize the form here if needed
    pass
