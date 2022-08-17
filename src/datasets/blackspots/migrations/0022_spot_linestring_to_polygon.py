# Generated by Django 3.2.14 on 2022-07-27 09:13

import django.contrib.gis.db.models.fields
from django.db import migrations
from django.contrib.gis.geos import Polygon


def line_string_to_polygon(apps, schema_editor):
    Spot = apps.get_model('blackspots', 'Spot')
    for spot in Spot.objects.all():
        if spot.polygoon is not None:
            spot.polygoon = Polygon((*spot.wegvak, spot.wegvak[0]))
            spot.save()


class Migration(migrations.Migration):

    dependencies = [
        ('blackspots', '0021_spot_point_nullable'),
    ]

    operations = [
        migrations.RenameField(
            model_name='spot',
            old_name='polygoon',
            new_name='wegvak',
        ),
        migrations.AddField(
            model_name='spot',
            name='polygoon',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
        migrations.RunPython(line_string_to_polygon),
    ]