# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-25 17:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tfoosball', '0008_auto_20161023_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='exphistory',
            name='match',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='exp_history', to='tfoosball.Match'),
            preserve_default=False,
        ),
    ]