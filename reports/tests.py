from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from reports.models import Report


class ReportAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.other_user = User.objects.create_user(username="other", password="pass12345")
        self.moderator = User.objects.create_user(username="moderator", password="pass12345")

        moderators_group, _ = Group.objects.get_or_create(name="Moderators")
        self.moderator.groups.add(moderators_group)

        self.report = Report.objects.create(
            title="Broken street light",
            description="Street light has been broken for several days.",
            location="Main square",
            contact_name="Owner Name",
            contact_phone="0123456789",
            user=self.owner,
        )

    def test_authenticated_user_create_uses_request_user(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            reverse("report-api-list-create"),
            data={
                "title": "Damaged sidewalk",
                "description": "A section of the sidewalk is damaged and unsafe.",
                "location": "Central park entrance",
                "status": Report.Status.OPEN,
                "contact_name": "Injected Name",
                "contact_phone": "1234567890",
                "user": self.other_user.pk,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_report = Report.objects.get(pk=response.data["id"])
        self.assertEqual(created_report.user, self.owner)

    def test_non_owner_non_moderator_cannot_update_report(self):
        self.client.force_authenticate(self.other_user)

        response = self.client.patch(
            reverse("report-api-detail", kwargs={"pk": self.report.pk}),
            data={"title": "Updated by stranger"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_update_report(self):
        self.client.force_authenticate(self.moderator)

        response = self.client.patch(
            reverse("report-api-detail", kwargs={"pk": self.report.pk}),
            data={"title": "Updated by moderator"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertEqual(self.report.title, "Updated by moderator")
