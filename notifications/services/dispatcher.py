import os
from notifications.models import Trigger, NotificationTemplate, ChannelType, NotificationLog
from notifications.services.email import EmailService
from notifications.services.webpush import WebPushService

class NotificationDispatcher:
    @classmethod
    def dispatch_single_template(cls, template: NotificationTemplate, user=None, context: dict = None) -> dict:
        """Sends a notification for ONLY one specific matrix cell/channel"""
        # Block WhatsApp or any unsupported channel completely
        if template.channel not in [ChannelType.EMAIL, ChannelType.WEB_PUSH]:
            return {"channel": template.channel, "status": "SKIPPED"}

        context = context or {}
        username = user.username if user else context.get("username", "CandidateUser")
        to_email = os.getenv("TEST_RECIPIENT_EMAIL", "test@example.com")

        # Dynamic variable replacement
        rendered_body = template.body.replace("{{username}}", username).replace("{{action}}", template.trigger.name)
        rendered_title = (template.title or f"{template.trigger.name} Notification").replace("{{username}}", username).replace("{{action}}", template.trigger.name)

        recipient = ""
        res = {"status": "FAILED", "error": "Unknown channel"}

        if template.channel == ChannelType.EMAIL:
            recipient = to_email
            res = EmailService.send(to_email=to_email, subject=rendered_title, body=rendered_body)

        elif template.channel == ChannelType.WEB_PUSH:
            recipient = "Desktop Web Browser"
            res = WebPushService.send(title=rendered_title, body=rendered_body)

        status = res.get("status", "FAILED")
        payload = str(res.get("response") or res.get("error"))

        # Log audit entry
        NotificationLog.objects.create(
            trigger_name=template.trigger.name,
            channel=template.channel,
            recipient=recipient,
            subject=rendered_title,
            message=rendered_body,
            status=status,
            response_payload=payload
        )

        return {"channel": template.channel, "status": status, "result": res}

    @classmethod
    def dispatch_trigger(cls, trigger_slug: str, user=None, context: dict = None) -> list:
        """Dispatches ONLY Email and Web Push for a trigger"""
        try:
            trigger = Trigger.objects.get(slug=trigger_slug, is_active=True)
        except Trigger.DoesNotExist:
            return [{"error": f"Trigger '{trigger_slug}' not found"}]

        results = []
        # Explicitly only pull enabled Email and Web Push templates
        enabled_templates = NotificationTemplate.objects.filter(
            trigger=trigger, 
            is_enabled=True,
            channel__in=[ChannelType.EMAIL, ChannelType.WEB_PUSH]
        )

        for tmpl in enabled_templates:
            res = cls.dispatch_single_template(tmpl, user=user, context=context)
            results.append(res)

        return results
