# Generated by Django 2.1.5 on 2019-01-28 10:35

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Spot",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("spot_id", models.CharField(max_length=16)),
                ("description", models.CharField(max_length=120)),
                ("point", django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ("stadsdeel", models.CharField(max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Voorbereiding", "Voorbereiding"),
                            ("Onderzoek_ontwerp", "Onderzoek/ ontwerp"),
                            ("Gereed", "Gereed"),
                            ("Geen_maatregel", "Geen maatregel"),
                            ("Uitvoering", "Uitvoering"),
                            ("Onbekend", "Onbekend"),
                        ],
                        max_length=32,
                    ),
                ),
                ("jaar_blackspotlijst", models.IntegerField(null=True)),
            ],
        ),
    ]
