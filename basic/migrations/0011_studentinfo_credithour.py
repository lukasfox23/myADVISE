# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-06 05:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0010_auto_20161201_0125'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentinfo',
            name='credithour',
            field=models.IntegerField(default=15),
            preserve_default=False,
        ),
    ]
