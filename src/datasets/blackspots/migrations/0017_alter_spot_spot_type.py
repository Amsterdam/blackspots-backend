# Generated by Django 3.2.13 on 2022-06-02 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blackspots', '0016_alter_spot_stadsdeel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spot',
            name='spot_type',
            field=models.CharField(choices=[('blackspot', 'blackspot'), ('wegvak', 'wegvak'), ('protocol ernstig', 'protocol ernstig'), ('protocol dodelijk', 'protocol dodelijk'), ('risico', 'risico'), ('gebiedslocatie ivm', 'gebiedslocatie ivm'), ('schoolstraat', 'schoolstraat'), ('vso', 'vso')], max_length=24),
        ),
    ]