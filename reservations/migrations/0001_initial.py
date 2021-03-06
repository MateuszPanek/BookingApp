# Generated by Django 3.0.3 on 2020-07-25 20:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('website', '0001_initial'),
        ('personnel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], default='1', max_length=9, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_hour', models.TimeField()),
                ('end_hour', models.TimeField()),
                ('availability_days', models.ManyToManyField(to='reservations.WorkDay')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='personnel.PersonnelProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True)),
                ('start_time', models.TimeField(blank=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='clients.ClientProfile')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='website.Service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='personnel.PersonnelProfile')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlySchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(choices=[('2020', 2020), ('2021', 2021)], default='1', max_length=4)),
                ('month', models.CharField(choices=[('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], default='1', max_length=9)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personnel.PersonnelProfile')),
            ],
        ),
        migrations.CreateModel(
            name='DailySchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('break_start', models.TimeField(blank=True, null=True)),
                ('break_end', models.TimeField(blank=True, null=True)),
                ('month', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.MonthlySchedule')),
            ],
        ),
    ]
