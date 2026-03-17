from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    name = "marketplace"

    def ready(self):
        from django.db.utils import OperationalError, ProgrammingError

        try:
            from .models import MarketplaceCategory
        except (OperationalError, ProgrammingError):
            return

        categories = [
            "Electronics",
            "Furniture",
            "Clothing",
            "Home & Garden",
            "Other",
        ]
        for name in categories:
            MarketplaceCategory.objects.get_or_create(name=name)
