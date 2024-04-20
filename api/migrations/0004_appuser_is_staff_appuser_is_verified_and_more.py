# Generated by Django 5.0.4 on 2024-04-20 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_appuser_email_alter_appuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
    ]
