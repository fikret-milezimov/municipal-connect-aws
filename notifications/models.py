

from django.conf import settings
from django.db import models

from reports.models import Report

User = settings.AUTH_USER_MODEL


class Notification(models.Model):

    class Meta:
        ordering = ['-created_at']

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")

    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}"