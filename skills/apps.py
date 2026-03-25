from django.apps import AppConfig


class SkillsConfig(AppConfig):
    name = "skills"

    def ready(self):
        from django.db.utils import OperationalError, ProgrammingError

        try:
            from .models import SkillCategory
            SkillCategory.objects.exists()
        except (OperationalError, ProgrammingError):
            return

        categories = [
            "IT & Programming",
            "Home Repair",
            "Cleaning Services",
            "Education & Tutoring",
            "Health & Fitness",
        ]

        for name in categories:
            SkillCategory.objects.get_or_create(name=name)