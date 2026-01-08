from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tag", "0003_remove_tag_deleted_at_alter_tag_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="tag",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
