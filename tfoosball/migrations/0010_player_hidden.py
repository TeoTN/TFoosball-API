# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-01 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tfoosball', '0009_exphistory_match'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
