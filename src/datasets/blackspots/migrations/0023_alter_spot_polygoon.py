# Generated by Django 3.2.13 on 2022-06-29 15:07

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blackspots', '0022_alter_spot_point'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spot',
            name='polygoon',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
    ]
