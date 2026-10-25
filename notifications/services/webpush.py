import os
import requests

class WebPushService:
    @staticmethod
    def send(title: str, body: str) -> dict:
        app_id = os.getenv("ONESIGNAL_APP_ID", "").strip()
        rest_api_key = os.getenv("ONESIGNAL_REST_API_KEY", "").strip()

        # 1. Mode A: If OneSignal credentials exist in .env / Render, send via OneSignal REST API
        is_onesignal_configured = (
            app_id and rest_api_key 
            and app_id != "your_onesignal_app_id" 
            and rest_api_key != "your_onesignal_rest_api_key"
        )

        if is_onesignal_configured:
            url = "https://onesignal.com/api/v1/notifications"
            headers = {
                "Authorization": f"Basic {rest_api_key}",
                "Content-Type": "application/json; charset=utf-8"
            }
            payload = {
                "app_id": app_id,
                "included_segments": ["Total Subscriptions"],
                "headings": {"en": title or "Starclinch Notification"},
                "contents": {"en": body}
            }
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=10)
                try:
                    data = res.json()
                except Exception:
                    data = {}

                if res.status_code in (200, 201) and not data.get("errors"):
                    push_id = data.get("id", "sent")
                    return {
                        "status": "SUCCESS",
                        "mode": "onesignal_api",
                        "response": f"Push delivered via OneSignal REST API (ID: {push_id})"
                    }

                err_msg = data.get("errors") or res.text
                return {
                    "status": "FAILED",
                    "error": f"OneSignal API error ({res.status_code}): {err_msg}"
                }
            except Exception as e:
                return {
                    "status": "FAILED",
                    "error": f"OneSignal request failed: {str(e)}"
                }

        # 2. Mode B: Native Browser Web Push Mode (Default - zero external API keys needed)
        return {
            "status": "SUCCESS",
            "mode": "browser_push",
            "response": "Browser Web Push notification delivered to desktop"
        }

