# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-20 04:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0002_auto_20160928_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlightPlan',
            fields=[
                ('flightplanID', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
            ],
        ),
    ]