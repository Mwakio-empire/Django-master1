import os
import django
from django.core.mail import send_mail

# Set the Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_store.settings')

# Initialize Django
django.setup()

# Send email
send_mail(
    'Test Email',
    'This is a test email.',
    'mikemwazo444@.com',
    ['to@example.com'],
    fail_silently=False,
)
