import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from notifications.services.email import EmailService
from notifications.models import NotificationLog

recipient = os.getenv("TEST_RECIPIENT_EMAIL")
print(f"--> Sending test email to: {recipient}...")

result = EmailService.send(
    to_email=recipient,
    subject="Starclinch Notification System Test",
    body="Hello! This is a real test notification from your Django notification system."
)

print("\n--- Result ---")
print(result)

if result.get("status") == "SUCCESS":
    print("\n SUCCESS! Check your Gmail inbox right now!")
    NotificationLog.objects.create(
        trigger_name="Manual Test",
        channel="email",
        recipient=recipient,
        subject="Starclinch Notification System Test",
        message="Test email notification",
        status="SUCCESS",
        response_payload=str(result.get("response"))
    )
else:
    print("\n Failed. Reason:", result.get("error"))
