# Generated by Django 5.1.2 on 2024-10-28 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelapp', '0009_remove_userprofile_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
