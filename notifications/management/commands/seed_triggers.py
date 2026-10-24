from django.core.management.base import BaseCommand
from notifications.models import Trigger, NotificationTemplate, ChannelType

class Command(BaseCommand):
    help = 'Seeds default triggers and templates from the PDF assignment'

    def handle(self, *args, **kwargs):
        # Triggers defined in Section 1 of the PDF
        triggers = [
            ("Login", "login", "User signs in on the website"),
            ("Logout", "logout", "User signs out of the website"),
            ("Not logged in for 1 day", "not-logged-in-1-day", "User has not visited the website for 24 hours"),
            ("Not logged in for 1 week", "not-logged-in-1-week", "User has not visited for 7 days"),
        ]

        defaults = {
            'whatsapp': "Welcome back, {{username}}! We are glad to see you",
            'email': "You have successfully performed {{action}} on your account.",
            'web_push': "Welcome back! Check your notifications."
        }

        created_triggers = 0
        created_templates = 0

        for name, slug, desc in triggers:
            trigger_obj, t_created = Trigger.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc}
            )
            if t_created:
                created_triggers += 1

            for channel in [ChannelType.WHATSAPP, ChannelType.EMAIL, ChannelType.WEB_PUSH]:
                _, tmpl_created = NotificationTemplate.objects.get_or_create(
                    trigger=trigger_obj,
                    channel=channel,
                    defaults={
                        'title': f"{name} Notification",
                        'body': defaults[channel],
                        'is_enabled': True
                    }
                )
                if tmpl_created:
                    created_templates += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded: {created_triggers} Triggers and {created_templates} Matrix Cell Templates!"
        ))
