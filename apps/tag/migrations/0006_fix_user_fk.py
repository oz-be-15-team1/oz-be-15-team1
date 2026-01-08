from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tag", "0004_tag_deleted_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="user",
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
