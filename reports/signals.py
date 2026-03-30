from django.db.models.signals import post_save
from django.dispatch import receiver
from reports.models import Report
from notifications.tasks import create_notifications_for_report


@receiver(post_save, sender=Report)
def report_created(sender, instance, created, **kwargs):
    if created:
        create_notifications_for_report(instance.id, instance.title, instance.user_id)
