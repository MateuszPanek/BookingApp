# Generated by Django 3.0.3 on 2020-07-26 08:30

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20200725_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='creation_date',
            field=models.DateField(default=datetime.datetime(2020, 7, 26, 8, 30, 8, 22078, tzinfo=utc)),
        ),
    ]
