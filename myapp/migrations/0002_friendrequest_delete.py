# Generated by Django 4.2 on 2024-06-03 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='delete',
            field=models.BooleanField(default=False),
        ),
    ]
