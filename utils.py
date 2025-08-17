# core/utils.py
from twilio.rest import Client
from django.conf import settings

def send_sms(to, message):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to
        )
        return True
    except Exception as e:
        print(f"SMS send failed: {e}")
        return False
