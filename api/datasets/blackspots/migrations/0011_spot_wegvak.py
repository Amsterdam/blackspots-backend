# Generated by Django 2.1.8 on 2019-04-29 12:37

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blackspots', '0010_auto_20190326_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='spot',
            name='wegvak',
            field=django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=4326),
        ),
    ]