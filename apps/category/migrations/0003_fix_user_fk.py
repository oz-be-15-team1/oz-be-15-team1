from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
    ("category", "0002_add_category_user"),
    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
]



    operations = [
        migrations.AlterField(
            model_name="category",
            name="user",
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
