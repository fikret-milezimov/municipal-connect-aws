from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from skills.forms import SkillUpdateForm
from skills.models import Skill


class SkillUpdatePermissionsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="pass12345",
            first_name="Regular",
            last_name="Owner",
        )
        self.content_manager = User.objects.create_user(
            username="manager",
            password="pass12345",
            first_name="Content",
            last_name="Manager",
        )
        content_manager_group, _ = Group.objects.get_or_create(name="ContentManagers")
        self.content_manager.groups.add(content_manager_group)

        self.skill = Skill.objects.create(
            name="Guitar lessons",
            description="Detailed enough description for validation.",
            level=Skill.Level.BEGINNER,
            contact_name="Original Contact",
            contact_phone="0123456789",
            user=self.owner,
        )

    def test_update_form_shows_disabled_created_at_and_locks_contact_name_for_regular_user(self):
        form = SkillUpdateForm(instance=self.skill, user=self.owner)

        self.assertTrue(form.fields["created_at"].disabled)
        self.assertEqual(form.fields["created_at"].initial, self.skill.created_at)
        self.assertTrue(form.fields["contact_name"].disabled)

    def test_regular_user_cannot_change_contact_name_via_post(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("skills:edit", kwargs={"pk": self.skill.pk}),
            data={
                "name": self.skill.name,
                "description": self.skill.description,
                "level": self.skill.level,
                "contact_name": "Hacked Name",
                "contact_phone": self.skill.contact_phone,
                "categories": [],
                "created_at": timezone.now().strftime("%d-%m-%Y %H:%M"),
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "skills:details",
                kwargs={"pk": self.skill.pk, "slug": self.skill.slug},
            ),
        )
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.contact_name, "Original Contact")

    def test_content_manager_can_change_contact_name(self):
        self.client.force_login(self.content_manager)

        response = self.client.post(
            reverse("skills:edit", kwargs={"pk": self.skill.pk}),
            data={
                "name": self.skill.name,
                "description": self.skill.description,
                "level": self.skill.level,
                "contact_name": "Updated By Manager",
                "contact_phone": self.skill.contact_phone,
                "categories": [],
                "created_at": timezone.now().strftime("%d-%m-%Y %H:%M"),
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "skills:details",
                kwargs={"pk": self.skill.pk, "slug": self.skill.slug},
            ),
        )
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.contact_name, "Updated By Manager")
