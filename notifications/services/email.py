import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

class EmailService:
    @staticmethod
    def send(to_email: str, subject: str, body: str) -> dict:
        sender = settings.DEFAULT_FROM_EMAIL or os.getenv('EMAIL_HOST_USER')
        
        if not sender or not settings.EMAIL_HOST_PASSWORD:
            return {"status": "FAILED", "error": "Gmail credentials missing in .env"}

        try:
            subject = subject or "Notification from Starclinch"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; color: #333; max-width: 600px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #2563eb; margin-top: 0;">{subject}</h2>
                <p style="font-size: 16px; line-height: 1.5;">{body}</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <small style="color: #888;">This is an automated notification from the Starclinch Notification System.</small>
            </div>
            """
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=sender,
                to=[to_email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            
            return {"status": "SUCCESS", "response": f"Email successfully delivered to {to_email}"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
