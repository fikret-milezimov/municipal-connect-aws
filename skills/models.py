from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils.text import slugify


phone_validator = RegexValidator(
    regex=r"^\d{10}$",
    message="Phone number must contain exactly 10 digits.",
)


class SkillCategory(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(3)],
    )

    def __str__(self):
        return self.name


class Skill(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "Beginner", "Beginner"
        INTERMEDIATE = "Intermediate", "Intermediate"
        ADVANCED = "Advanced", "Advanced"

    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
    )
    slug = models.SlugField()
    description = models.TextField(
        validators=[MinLengthValidator(10)],
    )
    level = models.CharField(
        max_length=15,
        choices=Level.choices,
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

    categories = models.ManyToManyField(
        SkillCategory,
        related_name="skills",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name or "")
        super().save(*args, **kwargs)
