# Generated by Django 4.1.1 on 2023-07-26 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailreport', '0010_alter_serials_is_commissioned'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_subscribed',
            field=models.BooleanField(default=True),
        ),
    ]
