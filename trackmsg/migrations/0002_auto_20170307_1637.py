# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-03-07 11:07
from __future__ import unicode_literals

from django.db import migrations
import trackmsg.models


class Migration(migrations.Migration):

    dependencies = [
        ('trackmsg', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='geo_fence',
            field=trackmsg.models.ListField(blank=True, help_text='list of pks of geo fences triggered', max_length=100, null=True),
        ),
    ]
