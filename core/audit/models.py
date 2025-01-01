from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
    ]

    MODULE_CHOICES = [
        ("USER", "User Management"),
        ("ROLE", "Role Management"),
        ("MENU", "Menu Management"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="audit_logs"
    )
    # User info to preserve after user deletion
    username = models.CharField(max_length=150)
    user_email = models.CharField(max_length=254, null=True)

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    module = models.CharField(max_length=20, choices=MODULE_CHOICES)
    resource_id = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    detail = models.JSONField()
    ip_address = models.GenericIPAddressField(null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True)
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "action", "module", "timestamp"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def save(self, *args, **kwargs):
        # Capture user info before saving
        if self.user and not self.username:
            self.username = self.user.username
            self.user_email = self.user.email
        super().save(*args, **kwargs)
