from django.db import migrations


def create_default_categories(apps, schema_editor):
    Category = apps.get_model("campaigns", "Category")
    for name in ("Tecnología", "Arte", "Comunidad"):
        Category.objects.get_or_create(name=name)


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model("campaigns", "Category")
    Category.objects.filter(name__in=("Tecnología", "Arte", "Comunidad")).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0003_campaign_update"),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]
