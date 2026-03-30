from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth import get_user_model
from django.db import models
from slugify import slugify


UserModel = get_user_model()


phone_validator = RegexValidator(
    regex=r"^\d{10}$",
    message="Phone number must contain exactly 10 digits.",
)


class MarketplaceCategory(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(3)],
    )

    def __str__(self):
        return self.name


class MarketplaceItem(models.Model):
    class Type(models.TextChoices):
        OFFER = "Offer", "Offer"
        WANTED = "Wanted", "Wanted"
        GIVEAWAY = "Giveaway", "Giveaway"

    class Condition(models.TextChoices):
        NEW = "New", "New"
        USED = "Used", "Used"

    title = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
    )
    slug = models.SlugField()

    description = models.TextField(
        validators=[MinLengthValidator(10)],
    )



    type = models.CharField(
        max_length=10,
        choices=Type.choices,
    )

    condition = models.CharField(
        max_length=20,
        choices=Condition.choices,
        blank=True,
        null=True,
    )

    contact_name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2)],
    )

    contact_phone = models.CharField(
        max_length=10,
        validators=[phone_validator],
    )

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="marketplace_items",
        blank=True,
        null=True,
    )

    category = models.ForeignKey(
        MarketplaceCategory,
        on_delete=models.CASCADE,
        related_name="items",
        blank=True,
        null=True,
    )

    image = models.ImageField(
        upload_to="marketplace/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
