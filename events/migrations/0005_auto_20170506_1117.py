# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-06 11:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20170505_1958'),
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
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='events.user'),
        ),
    ]