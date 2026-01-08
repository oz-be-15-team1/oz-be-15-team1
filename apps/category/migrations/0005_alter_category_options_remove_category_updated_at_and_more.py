from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0004_alter_category_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['sort_order', 'id']},
        ),

        # updated_at 컬럼이 이미 없을 수 있으니 DB는 IF EXISTS로 안전하게 처리하고,
        # Django state에서는 RemoveField를 적용
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "ALTER TABLE category_category DROP COLUMN IF EXISTS updated_at;",
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='category',
                    name='updated_at',
                ),
            ],
        ),

        migrations.AlterField(
            model_name='category',
            name='kind',
            field=models.CharField(choices=[('INCOME', 'INCOME'), ('EXPENSE', 'EXPENSE')], max_length=10),
        ),
        migrations.AlterField(
            model_name='category',
            name='sort_order',
            field=models.IntegerField(default=0),
        ),

        # 인덱스도 이미 존재할 수 있으니 DB는 IF NOT EXISTS로 안전하게 처리하고,
        # Django state에서는 AddIndex를 적용
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX IF NOT EXISTS category_ca_user_id_1c2f2b_idx "
                    "ON category_category (user_id, deleted_at);",
                    reverse_sql="DROP INDEX IF EXISTS category_ca_user_id_1c2f2b_idx;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX IF NOT EXISTS category_ca_user_id_7c90a0_idx "
                    "ON category_category (user_id, kind, deleted_at);",
                    reverse_sql="DROP INDEX IF EXISTS category_ca_user_id_7c90a0_idx;",
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name='category',
                    index=models.Index(fields=['user', 'deleted_at'], name='category_ca_user_id_1c2f2b_idx'),
                ),
                migrations.AddIndex(
                    model_name='category',
                    index=models.Index(fields=['user', 'kind', 'deleted_at'], name='category_ca_user_id_7c90a0_idx'),
                ),
            ],
        ),
    ]
