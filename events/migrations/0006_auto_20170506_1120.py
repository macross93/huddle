# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-06 11:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20170506_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='charity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.charity'),
        ),
        migrations.AlterField(
            model_name='event',
            name='volunteer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.user'),
        ),
    ]
