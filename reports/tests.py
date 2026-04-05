import json
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from marketplace.models import MarketplaceItem
from notifications.models import Notification
from reports.forms import ReportCreateForm, ReportUpdateForm
from reports.models import Report
from skills.models import Skill


class BaseReportTestCase(TestCase):
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
        self.owner = User.objects.create_user(
            username="owner",
            password="pass12345",
            first_name="Olivia",
            last_name="Owner",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="pass12345",
            first_name="Peter",
            last_name="Resident",
        )
        self.moderator = User.objects.create_user(
            username="moderator",
            password="pass12345",
            first_name="Mila",
            last_name="Moderator",
        )

        moderators_group, _ = Group.objects.get_or_create(name="Moderators")
        self.moderator.groups.add(moderators_group)

        self.report = Report.objects.create(
            title="Broken street light",
            description="The main street light has been broken for over a week.",
            location="Central square",
            contact_name="Olivia Owner",
            contact_phone="0123456789",
            user=self.owner,
        )

    def get_valid_report_data(self, **overrides):
        data = {
            "title": "Blocked drainage channel",
            "description": "The drainage channel is blocked and water is collecting after rain.",
            "location": "Ivan Vazov Street",
            "status": Report.Status.OPEN,
            "contact_name": "Olivia Owner",
            "contact_phone": "1234567890",
        }
        data.update(overrides)
        return data


class ReportModelTests(BaseReportTestCase):
    def test_report_str_returns_title(self):
        self.assertEqual(str(self.report), "Broken street light")

    def test_report_creation_generates_slug_and_default_status(self):
        report = Report.objects.create(
            title="Damaged bus stop",
            description="The shelter panels are broken and the bench is damaged.",
            location="City bus station",
            contact_name="Peter Resident",
            contact_phone="1112223333",
            user=self.other_user,
        )

        self.assertEqual(report.slug, "damaged-bus-stop")
        self.assertEqual(report.status, Report.Status.OPEN)
        self.assertTrue(report.is_active)

    def test_skill_str_returns_name(self):
        skill = Skill.objects.create(
            name="First aid lessons",
            description="Weekly first aid lessons for residents and volunteers.",
            level=Skill.Level.BEGINNER,
            contact_name="Mila Moderator",
            contact_phone="2223334444",
            user=self.moderator,
        )

        self.assertEqual(str(skill), "First aid lessons")

    def test_marketplace_item_str_returns_title(self):
        item = MarketplaceItem.objects.create(
            title="Used office chair",
            description="Comfortable office chair in good condition for home or office use.",
            type=MarketplaceItem.Type.OFFER,
            condition=MarketplaceItem.Condition.USED,
            contact_name="Olivia Owner",
            contact_phone="3334445555",
            user=self.owner,
        )

        self.assertEqual(str(item), "Used office chair")

    def test_notification_str_returns_user_reference(self):
        notification = Notification.objects.create(
            user=self.owner,
            report=self.report,
            message="Your report has a new update.",
        )

        self.assertEqual(str(notification), f"Notification for {self.owner}")

    def test_profile_is_created_for_new_user(self):
        self.assertTrue(Profile.objects.filter(user=self.owner).exists())


class ReportViewTests(BaseReportTestCase):
    def test_report_list_view_returns_success_and_uses_template(self):
        response = self.client.get(reverse("reports:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/report-list.html")
        self.assertContains(response, self.report.title)

    def test_report_detail_view_returns_success_and_uses_template(self):
        response = self.client.get(
            reverse("reports:details", kwargs={"pk": self.report.pk, "slug": self.report.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/report-details.html")
        self.assertEqual(response.context["report"], self.report)

    def test_report_detail_view_redirects_to_canonical_slug(self):
        response = self.client.get(
            reverse("reports:details", kwargs={"pk": self.report.pk, "slug": "wrong-slug"})
        )

        self.assertRedirects(
            response,
            reverse("reports:details", kwargs={"pk": self.report.pk, "slug": self.report.slug}),
        )

    def test_report_create_view_creates_report_and_redirects_after_post(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("reports:create"), data=self.get_valid_report_data())

        self.assertRedirects(response, reverse("reports:list"))
        self.assertTrue(Report.objects.filter(title="Blocked drainage channel", user=self.owner).exists())

    def test_report_update_view_owner_can_update_report_and_redirect(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("reports:edit", kwargs={"pk": self.report.pk}),
            data={
                "title": "Broken street light near school",
                "description": self.report.description,
                "location": self.report.location,
                "status": Report.Status.RESOLVED,
                "contact_name": "Changed Name",
                "contact_phone": self.report.contact_phone,
            },
        )

        self.assertRedirects(
            response,
            reverse("reports:details", kwargs={"pk": self.report.pk, "slug": self.report.slug}),
        )
        self.report.refresh_from_db()
        self.assertEqual(self.report.title, "Broken street light near school")
        self.assertEqual(self.report.status, Report.Status.OPEN)
        self.assertEqual(self.report.contact_name, "Olivia Owner")

    def test_report_delete_view_owner_can_delete_report_and_redirect(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("reports:delete", kwargs={"pk": self.report.pk}))

        self.assertRedirects(response, reverse("reports:list"))
        self.assertFalse(Report.objects.filter(pk=self.report.pk).exists())

    def test_my_reports_view_returns_only_logged_in_user_reports(self):
        Report.objects.create(
            title="Overflowing trash bin",
            description="The trash bin has been overflowing since the weekend.",
            location="School entrance",
            contact_name="Peter Resident",
            contact_phone="9998887777",
            user=self.other_user,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("reports:my-reports"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/my-reports.html")
        self.assertEqual(list(response.context["reports"]), [self.report])


class ReportPermissionTests(BaseReportTestCase):
    def test_anonymous_user_is_redirected_from_create_view(self):
        response = self.client.get(reverse("reports:create"))

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('reports:create')}")

    def test_anonymous_user_is_redirected_from_my_reports_view(self):
        response = self.client.get(reverse("reports:my-reports"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('reports:my-reports')}",
        )

    def test_non_owner_cannot_edit_report(self):
        self.client.force_login(self.other_user)

        response = self.client.get(reverse("reports:edit", kwargs={"pk": self.report.pk}))

        self.assertEqual(response.status_code, 404)

    def test_non_owner_cannot_delete_report(self):
        self.client.force_login(self.other_user)

        response = self.client.get(reverse("reports:delete", kwargs={"pk": self.report.pk}))

        self.assertEqual(response.status_code, 404)

    def test_moderator_can_edit_other_users_report(self):
        self.client.force_login(self.moderator)

        response = self.client.post(
            reverse("reports:edit", kwargs={"pk": self.report.pk}),
            data={
                "title": self.report.title,
                "description": self.report.description,
                "location": self.report.location,
                "status": Report.Status.RESOLVED,
                "contact_name": "Mila Moderator",
                "contact_phone": self.report.contact_phone,
            },
        )

        self.assertRedirects(
            response,
            reverse("reports:details", kwargs={"pk": self.report.pk, "slug": self.report.slug}),
        )
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.RESOLVED)
        self.assertEqual(self.report.contact_name, "Mila Moderator")


class ReportFormTests(BaseReportTestCase):
    def test_report_create_form_is_invalid_with_missing_required_fields(self):
        form = ReportCreateForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("description", form.errors)
        self.assertIn("location", form.errors)
        self.assertIn("contact_name", form.errors)
        self.assertIn("contact_phone", form.errors)

    def test_report_create_form_returns_phone_validation_error_message(self):
        form = ReportCreateForm(
            data=self.get_valid_report_data(contact_phone="12345")
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["contact_phone"],
            ["Phone number must contain exactly 10 digits."],
        )

    def test_report_create_form_returns_title_min_length_error(self):
        form = ReportCreateForm(
            data=self.get_valid_report_data(title="Road")
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["title"],
            ["Ensure this value has at least 5 characters (it has 4)."],
        )

    def test_report_update_form_disables_status_and_contact_name_for_regular_user(self):
        form = ReportUpdateForm(instance=self.report, user=self.owner)

        self.assertTrue(form.fields["status"].disabled)
        self.assertTrue(form.fields["contact_name"].disabled)


class ReportAPITests(BaseReportTestCase):
    def test_api_list_endpoint_returns_reports(self):
        response = self.client.get(reverse("report-api-list-create"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["title"], self.report.title)

    def test_api_create_requires_authentication(self):
        response = self.client.post(
            reverse("report-api-list-create"),
            data=json.dumps(self.get_valid_report_data()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_api_authenticated_user_creates_report_as_request_user(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("report-api-list-create"),
            data=json.dumps({**self.get_valid_report_data(), "user": self.other_user.pk}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        created_report = Report.objects.get(pk=response.json()["id"])
        self.assertEqual(created_report.user, self.owner)

    def test_api_non_owner_cannot_update_report(self):
        self.client.force_login(self.other_user)

        response = self.client.patch(
            reverse("report-api-detail", kwargs={"pk": self.report.pk}),
            data=json.dumps({"title": "Updated by stranger"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_api_moderator_can_update_report(self):
        self.client.force_login(self.moderator)

        response = self.client.patch(
            reverse("report-api-detail", kwargs={"pk": self.report.pk}),
            data=json.dumps({"title": "Updated by moderator"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.report.refresh_from_db()
        self.assertEqual(self.report.title, "Updated by moderator")
