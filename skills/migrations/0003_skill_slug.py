from django.db import migrations, models
from slugify import slugify


def populate_skill_slug(apps, schema_editor):
    Skill = apps.get_model("skills", "Skill")
    for skill in Skill.objects.all().only("id", "name", "slug"):
        if not skill.slug:
            skill.slug = slugify(skill.name)
            skill.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("skills", "0002_alter_skill_level"),
    ]

    operations = [
        migrations.AddField(
            model_name="skill",
            name="slug",
            field=models.SlugField(blank=True),
        ),
        migrations.RunPython(populate_skill_slug, migrations.RunPython.noop),
    ]
