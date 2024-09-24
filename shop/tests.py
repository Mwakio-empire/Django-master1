from django.test import TestCase

# Create your tests here.
# tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Product, Comment
from .forms import SignUpForm, CommentForm

class SignUpFormTest(TestCase):
    def test_valid_form(self):
        form_data = {'username': 'testuser', 'email': 'test@example.com', 'password1': 'password', 'password2': 'password'}
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {'username': 'testuser', 'email': 'test@example.com', 'password1': 'password', 'password2': 'differentpassword'}
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

class CommentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Test Product', description='A great product', price=10.00)
        self.client.login(username='testuser', password='password')

    def test_add_comment(self):
        response = self.client.post('/add_comment/', {'product_id': self.product.id, 'rating': 5, 'text': 'Great!'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(product=self.product, user=self.user).exists())
