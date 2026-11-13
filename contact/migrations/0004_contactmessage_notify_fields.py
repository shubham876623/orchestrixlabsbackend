from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0003_alter_contactmessage_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='notify_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('sent', 'Sent'),
                    ('failed', 'Failed'),
                    ('skipped', 'Skipped'),
                ],
                default='pending',
                help_text='Tracks whether founder email notification succeeded.',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='notify_error',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
