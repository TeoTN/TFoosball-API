# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-23 13:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tfoosball', '0004_auto_20161023_0008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='att_ratio',
        ),
        migrations.RemoveField(
            model_name='player',
            name='def_ratio',
        ),
        migrations.RemoveField(
            model_name='player',
            name='win_ratio',
        ),
        migrations.AddField(
            model_name='player',
            name='lost',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='played',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='won',
            field=models.IntegerField(default=0),
        ),
    ]