from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tag", "0002_remove_tag_updated_at_tag_color_tag_user"),
        ("transaction", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="tags",
            field=models.ManyToManyField(blank=True, related_name="transactions", to="tag.tag"),
        ),
    ]
