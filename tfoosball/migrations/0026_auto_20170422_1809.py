# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-22 18:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tfoosball', '0025_auto_20170406_1140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='hidden',
        ),
        migrations.AddField(
            model_name='member',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
