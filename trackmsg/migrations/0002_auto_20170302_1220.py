# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-03-02 12:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('trackmsg', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='alerted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='coordinate',
            field=models.CharField(default=(1, 2), help_text='cocatenated tuple of coordinates delimited \t\tby ,', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='geo_fence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trackmsg.GeoFence'),
        ),
        migrations.AddField(
            model_name='message',
            name='timestamp',
            field=models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='tracker',
            name='active',
            field=models.BooleanField(default=False, help_text='Sets this tracker to active tracking'),
        ),
        migrations.AddField(
            model_name='tracker',
            name='created',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='tracker',
            name='geo_fences',
            field=models.ManyToManyField(to='trackmsg.GeoFence'),
        ),
        migrations.AddField(
            model_name='tracker',
            name='tag',
            field=models.CharField(default='tag-1', help_text='tag name for tracker, \t\thas to be unique and can only contain characters, underscores and numbers', max_length=50, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tracker',
            name='url',
            field=models.SlugField(default='tag-1', help_text='the url for this tracker will be /track/<url>', unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='geofence',
            name='vertices',
            field=models.CharField(help_text="Concatenated list of vertices delimited by ':' , coordinates of a \t\t\tvertex are delimited by ','", max_length=300),
        ),
    ]