from celery import shared_task
from django.core.mail import send_mail
from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification
from reports.models import Report

User = get_user_model()


@shared_task
def create_notifications_for_report(report_id, report_title, creator_user_id):

    report = Report.objects.get(id=report_id)
    users = User.objects.exclude(id=creator_user_id)


    for user in users:
        Notification.objects.create(
            user=user,
            report=report,
            message=report_title
        )



@shared_task
def send_welcome_email(user_email):
    send_mail(
        subject='Welcome to Municipal Connect',
        message='Thank you for registering!',
        from_email='your_email@gmail.com',
        recipient_list=[user_email],
        fail_silently=False,
    )