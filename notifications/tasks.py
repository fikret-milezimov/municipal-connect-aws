# notifications/tasks.py

from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification
from reports.models import Report

User = get_user_model()


@shared_task
def create_notifications_for_report(report_id, report_title, creator_user_id):
    report = Report.objects.get(id=report_id)
    users = User.objects.exclude(id=creator_user_id)

    notifications = [
        Notification(
            user=user,
            report = report,
            message= f"{report_title}"
        )
        for user in users
    ]

    Notification.objects.bulk_create(notifications)
