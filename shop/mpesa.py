# shop/mpesa.py

import base64
import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

def get_token():
    """Get the access token for MPesa API."""
    api_url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    response.raise_for_status()
    return response.json().get('access_token')

def initiate_payment(phone_number, amount):
    """Initiate the payment request to MPesa."""
    access_token = get_token()
    api_url = f"{settings.MPESA_BASE_URL}{settings.MPESA_LIPA_NGWE_ENDPOINT}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": base64.b64encode(f"{settings.MPESA_SHORTCODE}:{settings.MPESA_PASSKEY}".encode()).decode(),
        "Timestamp": datetime.now().strftime('%Y%m%d%H%M%S'),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "http://yourdomain.com/mpesa/callback/",
        "AccountReference": "JewelleryPurchase",
        "TransactionDesc": "Payment for purchase"
    }
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
