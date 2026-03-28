from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from marketplace.forms import MarketplaceUpdateForm
from marketplace.models import MarketplaceItem


class MarketplaceUpdatePermissionsTests(TestCase):
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

        self.item = MarketplaceItem.objects.create(
            title="Used bike",
            description="Detailed enough description for validation.",
            type=MarketplaceItem.Type.OFFER,
            condition=MarketplaceItem.Condition.USED,
            contact_name="Original Contact",
            contact_phone="0123456789",
            user=self.owner,
        )

    def test_update_form_shows_disabled_created_at_and_locks_contact_name_for_regular_user(self):
        form = MarketplaceUpdateForm(instance=self.item, user=self.owner)

        self.assertTrue(form.fields["created_at"].disabled)
        self.assertEqual(form.fields["created_at"].initial, self.item.created_at)
        self.assertTrue(form.fields["contact_name"].disabled)

    def test_regular_user_cannot_change_contact_name_via_post(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("marketplace:edit", kwargs={"pk": self.item.pk}),
            data={
                "title": self.item.title,
                "description": self.item.description,
                "type": self.item.type,
                "condition": self.item.condition,
                "contact_name": "Hacked Name",
                "contact_phone": self.item.contact_phone,
                "category": "",
                "created_at": timezone.now().strftime("%d-%m-%Y %H:%M"),
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "marketplace:details",
                kwargs={"pk": self.item.pk, "slug": self.item.slug},
            ),
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.contact_name, "Original Contact")

    def test_content_manager_can_change_contact_name(self):
        self.client.force_login(self.content_manager)

        response = self.client.post(
            reverse("marketplace:edit", kwargs={"pk": self.item.pk}),
            data={
                "title": self.item.title,
                "description": self.item.description,
                "type": self.item.type,
                "condition": self.item.condition,
                "contact_name": "Updated By Manager",
                "contact_phone": self.item.contact_phone,
                "category": "",
                "created_at": timezone.now().strftime("%d-%m-%Y %H:%M"),
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "marketplace:details",
                kwargs={"pk": self.item.pk, "slug": self.item.slug},
            ),
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.contact_name, "Updated By Manager")
