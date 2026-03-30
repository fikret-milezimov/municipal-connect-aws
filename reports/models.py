from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from slugify import slugify
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class Report(models.Model):
    class Status(models.TextChoices):
        OPEN = "Open", "Open"
        IN_PROGRESS = "In Progress", "In Progress"
        RESOLVED = "Resolved", "Resolved"

    title = models.CharField(
        max_length=120,
        validators=[MinLengthValidator(5)]
    )
    slug = models.SlugField()

    description = models.TextField(
        validators=[MinLengthValidator(10)]
    )

    location = models.CharField(
        max_length=150,
        validators=[MinLengthValidator(3)]
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN,
    )

    contact_name = models.CharField(max_length=50)
    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must contain exactly 10 digits."
    )

    contact_phone = models.CharField(
        max_length=10,
        validators=[phone_validator]
    )

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="reports",
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_active(self):
        return self.status != self.Status.RESOLVED

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):

        if not self.pk:
            if self.status != self.Status.OPEN:
                raise ValidationError({
                    "status": "New reports must start with 'Open' status."
                })

        if self.status == self.Status.RESOLVED and len(self.description) < 20:
            raise ValidationError({
                "description": "Resolved reports must have at least 20 characters."
            })

