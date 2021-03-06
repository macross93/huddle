# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-17 19:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_auto_20170507_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='confirmed',
            field=models.CharField(default='n', max_length=1),
        ),
        migrations.AlterField(
            model_name='event',
            name='charity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.charity'),
        ),
    ]
