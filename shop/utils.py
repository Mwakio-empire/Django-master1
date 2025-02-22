from django.contrib import messages  # Correctly import the messages module
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from uuid import uuid4
from .models import UserProfile

from django.core.mail import EmailMessage
from uuid import uuid4
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib import messages  # Correctly import the messages module
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from uuid import uuid4
from .models import UserProfile

from django.core.mail import EmailMessage
from uuid import uuid4
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

from .models import UserProfile

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from uuid import uuid4

def send_verification_email(request, user):
    verification_code = str(uuid4())

    try:
        # Update user profile with verification code
        profile = UserProfile.objects.get(user=user)
        profile.email_verification_code = verification_code
        profile.save()

        # Prepare email content
        current_site = get_current_site(request)
        verification_link = f"http://{current_site.domain}/verify/{verification_code}/"
        subject = "Verify Your Email Address"
        email_content = render_to_string('emails/verification_email.html', {
            'user': user,
            'verification_link': verification_link,
        })

        # Send email
        email = EmailMessage(
            subject=subject,
            body=email_content,
            from_email='noreply@yourdomain.com',
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send()

    except ObjectDoesNotExist:
        raise Exception("UserProfile does not exist for the user.")
