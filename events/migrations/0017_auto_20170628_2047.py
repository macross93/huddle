# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-28 20:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_auto_20170628_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='charity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.charity'),
        ),
        migrations.AlterField(
            model_name='event',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(upload_to='photos/'),
        ),
    ]