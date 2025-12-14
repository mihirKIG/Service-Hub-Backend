# Generated manually on 2025-12-09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_google_uid'),
    ]

    operations = [
        # Remove old columns that don't exist in the model
        migrations.RunSQL(
            sql="""
                ALTER TABLE users DROP COLUMN IF EXISTS user_type;
                ALTER TABLE users DROP COLUMN IF EXISTS auth_provider;
                ALTER TABLE users DROP COLUMN IF EXISTS address;
                ALTER TABLE users DROP COLUMN IF EXISTS updated_at;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]
