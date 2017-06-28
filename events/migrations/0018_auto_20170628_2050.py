# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-28 20:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_auto_20170628_2047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='duration',
        ),
        migrations.AlterField(
            model_name='event',
            name='charity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.charity'),
        ),
    ]
