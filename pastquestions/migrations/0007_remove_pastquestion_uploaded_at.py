# Generated by Django 5.2.1 on 2025-06-01 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastquestions', '0006_remove_pastquestion_download_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pastquestion',
            name='uploaded_at',
        ),
    ]
