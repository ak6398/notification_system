import os
import requests
from django.conf import settings

class EmailService:
    @staticmethod
    def send(to_email: str, subject: str, body: str) -> dict:
        subject = subject or "Notification from Starclinch"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; color: #333; max-width: 600px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #2563eb; margin-top: 0;">{subject}</h2>
            <p style="font-size: 16px; line-height: 1.5;">{body}</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <small style="color: #888;">This is an automated notification from the Starclinch Notification System.</small>
        </div>
        """

        resend_key = os.getenv("RESEND_API_KEY", "").strip()
        if not resend_key:
            return {
                "status": "FAILED",
                "error": "RESEND_API_KEY is missing. Please add RESEND_API_KEY to your .env file or Render Environment Variables."
            }

        # Resend default testing sender: "onboarding@resend.dev"
        sender = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev").strip()

        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": sender,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content,
                    "text": body
                },
                timeout=10
            )

            try:
                data = resp.json()
            except Exception:
                data = {}

            if resp.status_code in (200, 201):
                email_id = data.get("id", "sent")
                return {
                    "status": "SUCCESS",
                    "response": f"Email successfully delivered to {to_email} via Resend (ID: {email_id})"
                }

            # Return clear error message from Resend API (e.g. if testing to an unverified email address on free tier)
            err_msg = data.get("message") or resp.text
            return {"status": "FAILED", "error": f"Resend API error: {err_msg}"}

        except Exception as e:
            return {"status": "FAILED", "error": f"Resend connection failed: {str(e)}"}
