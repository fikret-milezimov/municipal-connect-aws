from django.db import migrations, models
from slugify import slugify


def populate_report_slug(apps, schema_editor):
    Report = apps.get_model("reports", "Report")
    for report in Report.objects.all().only("id", "title", "slug"):
        if not report.slug:
            report.slug = slugify(report.title)
            report.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0002_alter_report_contact_phone_alter_report_description_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="slug",
            field=models.SlugField(blank=True),
        ),
        migrations.RunPython(populate_report_slug, migrations.RunPython.noop),
    ]
