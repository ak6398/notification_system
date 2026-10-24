from django.db import models

class Trigger(models.Model):
    name = models.CharField(max_length=100)                     # e.g., "Login"
    slug = models.SlugField(max_length=100, unique=True)         # e.g., "login"
    description = models.TextField(blank=True, null=True)        # , "User signs in on the website"e.g.
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ChannelType(models.TextChoices):
    WHATSAPP = 'whatsapp', 'WhatsApp'
    EMAIL = 'email', 'Email'
    WEB_PUSH = 'web_push', 'Web Push'


class NotificationTemplate(models.Model):
    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE, related_name='templates')
    channel = models.CharField(max_length=20, choices=ChannelType.choices)
    title = models.CharField(max_length=255, blank=True, null=True) # Email subject or Web Push title
    body = models.TextField()                                        # Message content / template body
    is_enabled = models.BooleanField(default=True)                  # On/Off Toggle (cell requirement)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('trigger', 'channel')

    def __str__(self):
        return f"{self.trigger.name} - {self.channel}"


class NotificationLog(models.Model):
    trigger_name = models.CharField(max_length=100)
    channel = models.CharField(max_length=20)
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=50) # 'SUCCESS' or 'FAILED'
    response_payload = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.sent_at:%Y-%m-%d %H:%M}] {self.trigger_name} via {self.channel} -> {self.status}"
