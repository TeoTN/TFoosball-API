# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-06 23:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tfoosball', '0014_exphistorylegacy'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('exp', models.IntegerField()),
                ('match', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exp_history', to='tfoosball.MatchLegacy')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exp_history', to='tfoosball.Member')),
            ],
        ),
        migrations.AlterField(
            model_name='exphistorylegacy',
            name='match',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exp_history_legacy', to='tfoosball.MatchLegacy'),
        ),
        migrations.AlterField(
            model_name='exphistorylegacy',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exp_history_legacy', to=settings.AUTH_USER_MODEL),
        ),
    ]
