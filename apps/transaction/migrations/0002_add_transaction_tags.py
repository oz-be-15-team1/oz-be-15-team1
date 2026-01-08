from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tag", "0004_add_tag_deleted_at"),
        ("transaction", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="tags",
            field=models.ManyToManyField(blank=True, related_name="transactions", to="tag.tag"),
        ),
    ]
