from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notifications.models import Notification
from notifications.tasks import create_notifications_for_report
from reports.models import Report


class NotificationViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="maria",
            password="pass12345",
        )
        self.other_user = User.objects.create_user(
            username="ivan",
            password="pass12345",
        )

        self.report = Report.objects.create(
            title="Street light issue",
            description="The street light in front of the school is not working.",
            location="Central avenue",
            contact_name="Maria",
            contact_phone="0123456789",
            user=self.user,
        )

        self.notifications = [
            Notification.objects.create(
                user=self.user,
                message=f"Notification {index}",
                report=self.report if index % 2 == 0 else None,
            )
            for index in range(4)
        ]

    def test_profile_shows_latest_three_notifications(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        latest_notifications = list(response.context["latest_notifications"])
        self.assertEqual(len(latest_notifications), 3)
        self.assertEqual(
            [notification.pk for notification in latest_notifications],
            [notification.pk for notification in self.notifications[::-1][:3]],
        )

    def test_profile_notifications_page_lists_all_user_notifications_newest_first(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("notifications:profile-notifications"))

        self.assertEqual(response.status_code, 200)
        object_list = list(response.context["object_list"])
        self.assertEqual(
            [notification.pk for notification in object_list],
            list(
                Notification.objects.filter(user=self.user)
                .order_by("-created_at")
                .values_list("pk", flat=True)
            ),
        )

    def test_mark_as_read_updates_notification_and_redirects_to_next(self):
        self.client.force_login(self.user)
        unread_notification = self.notifications[0]

        response = self.client.get(
            reverse("notifications:read", kwargs={"pk": unread_notification.pk}),
            {"next": reverse("notifications:profile-notifications")},
        )

        unread_notification.refresh_from_db()
        self.assertTrue(unread_notification.is_read)
        self.assertRedirects(response, reverse("notifications:profile-notifications"))

    def test_delete_notification_removes_notification_and_redirects_to_next(self):
        self.client.force_login(self.user)
        notification = self.notifications[0]

        confirmation_response = self.client.get(
            reverse("notifications:delete", kwargs={"pk": notification.pk}),
            {"next": reverse("notifications:profile-notifications")},
        )

        self.assertEqual(confirmation_response.status_code, 200)

        response = self.client.post(
            reverse("notifications:delete", kwargs={"pk": notification.pk}),
            {"next": reverse("notifications:profile-notifications")},
        )

        self.assertFalse(Notification.objects.filter(pk=notification.pk).exists())
        self.assertRedirects(response, reverse("notifications:profile-notifications"))

    def test_user_only_sees_own_notifications(self):
        Notification.objects.create(
            user=self.other_user,
            message="Other user notification",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("notifications:profile-notifications"))

        self.assertEqual(response.status_code, 200)
        expected_ids = set(Notification.objects.filter(user=self.user).values_list("pk", flat=True))
        response_ids = {notification.pk for notification in response.context["object_list"]}
        self.assertEqual(response_ids, expected_ids)


class NotificationTaskTests(TestCase):
    def test_report_creator_does_not_receive_notification(self):
        creator = User.objects.create_user(username="creator", password="pass12345")
        recipient = User.objects.create_user(username="recipient", password="pass12345")

        report = Report.objects.create(
            title="Water leak near school",
            description="There is a persistent water leak near the school entrance.",
            location="North district",
            contact_name="Creator",
            contact_phone="0123456789",
            user=creator,
        )
        Notification.objects.all().delete()

        create_notifications_for_report(report.id, report.title, creator.id)

        self.assertFalse(Notification.objects.filter(user=creator, report=report).exists())
        self.assertTrue(Notification.objects.filter(user=recipient, report=report).exists())
