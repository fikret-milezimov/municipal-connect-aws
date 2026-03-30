from django.db import migrations, models
from slugify import slugify


def populate_marketplace_item_slug(apps, schema_editor):
    MarketplaceItem = apps.get_model("marketplace", "MarketplaceItem")
    for item in MarketplaceItem.objects.all().only("id", "title", "slug"):
        if not item.slug:
            item.slug = slugify(item.title)
            item.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0003_alter_marketplaceitem_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="marketplaceitem",
            name="slug",
            field=models.SlugField(blank=True),
        ),
        migrations.RunPython(populate_marketplace_item_slug, migrations.RunPython.noop),
    ]
