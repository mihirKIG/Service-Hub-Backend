from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='google_uid',
            field=models.CharField(
                max_length=255,
                unique=True,
                null=True,
                blank=True,
                help_text='Google User ID for Google Sign-In'
            ),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['google_uid'], name='users_google_uid_idx'),
        ),
    ]
