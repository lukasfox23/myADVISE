# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-19 22:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0006_auto_20161119_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentinfo',
            name='schedule',
            field=models.TextField(default='none'),
            preserve_default=False,
        ),
    ]