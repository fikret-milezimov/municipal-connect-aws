from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notifications.models import Notification
from reports.models import Report


class UnreadNotificationsContextProcessorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.notification_task_patcher = patch("reports.signals.create_notifications_for_report.delay")
        cls.mock_notification_delay = cls.notification_task_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.notification_task_patcher.stop()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="maria",
            password="pass12345",
        )
        self.report = Report.objects.create(
            title="Pothole near school",
            description="A large pothole near the school entrance needs urgent repair.",
            location="School entrance",
            contact_name="Maria",
            contact_phone="0123456789",
            user=self.user,
        )

    def test_home_context_sets_has_unread_notifications_false_for_anonymous_user(self):
        response = self.client.get(reverse("common:home"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_unread_notifications"])

    def test_home_context_sets_has_unread_notifications_true_for_authenticated_user(self):
        Notification.objects.create(
            user=self.user,
            report=self.report,
            message="Your report was reviewed.",
            is_read=False,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("common:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["has_unread_notifications"])
