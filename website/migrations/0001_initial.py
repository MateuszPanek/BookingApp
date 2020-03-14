# Generated by Django 3.0.3 on 2020-03-12 18:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactFormMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('message', models.TextField(max_length=5000)),
                ('sender', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('sending_date', models.DateTimeField(default=datetime.datetime(2020, 3, 12, 18, 50, 47, 901970, tzinfo=utc))),
                ('contact_consent', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.IntegerField()),
                ('duration', models.IntegerField()),
            ],
        ),
    ]