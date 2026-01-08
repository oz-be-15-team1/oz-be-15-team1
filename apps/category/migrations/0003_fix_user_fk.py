from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("category", "0002_alter_category_options_remove_category_updated_at_and_more"),  # 실제 마지막 migration 이름에 맞추세요
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="user",
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
