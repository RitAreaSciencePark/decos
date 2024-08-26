# Generated by Django 5.1 on 2024-08-26 14:55

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PRP_CDM_app', '0053_alter_administration_sr_id_alter_lagesample_sr_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administration',
            name='sr_id',
            field=models.CharField(default=uuid.UUID('7ef15af9-7d69-499e-bfa3-7a15411b89fa'), max_length=37, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='lagesample',
            name='sr_id',
            field=models.CharField(default=uuid.UUID('f02f4fe4-263f-4e23-868e-43f0916ee323'), max_length=37, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='lagesamples',
            name='reagents_date_of_delivery',
            field=models.DateField(blank=True, null=True),
        ),
    ]
