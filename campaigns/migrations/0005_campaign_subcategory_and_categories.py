from django.db import migrations, models


CATEGORY_NAMES = (
    "Tecnología e Innovación",
    "Arte y Cultura",
    "Entretenimiento y Juegos",
    "Diseño y Estilo de Vida",
    "Negocios, Finanzas e Impacto",
    "Causas Sociales y Comunidad",
)


def seed_categories(apps, schema_editor):
    Category = apps.get_model("campaigns", "Category")
    renames = {
        "Tecnología": "Tecnología e Innovación",
        "Arte": "Arte y Cultura",
        "Comunidad": "Causas Sociales y Comunidad",
    }
    for old_name, new_name in renames.items():
        Category.objects.filter(name=old_name).update(name=new_name)
    for name in CATEGORY_NAMES:
        Category.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0004_seed_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="subcategory",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
