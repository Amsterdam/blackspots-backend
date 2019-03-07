# Generated by Django 2.1.5 on 2019-03-06 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blackspots', '0003_spot_spot_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Ontwerp', 'Ontwerp'), ('Rapportage', 'Rapportage')], max_length=16)),
                ('filename', models.CharField(max_length=128)),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='blackspots.Spot')),
            ],
        ),
    ]
