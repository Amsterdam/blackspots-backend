# Generated by Django 3.2.13 on 2022-07-13 09:41

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blackspots", "0020_rename_wegvak_spot_polygoon"),
    ]

    operations = [
        migrations.AlterField(
            model_name="spot",
            name="point",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
    ]
