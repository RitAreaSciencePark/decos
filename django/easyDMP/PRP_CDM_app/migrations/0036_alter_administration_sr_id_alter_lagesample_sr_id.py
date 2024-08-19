# Generated by Django 5.1 on 2024-08-19 09:49

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PRP_CDM_app', '0035_alter_administration_sr_id_alter_lagesample_sr_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administration',
            name='sr_id',
            field=models.CharField(default=uuid.UUID('150f690a-28a7-4a87-a1c4-d741d18ba616'), max_length=37, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='lagesample',
            name='sr_id',
            field=models.CharField(default=uuid.UUID('ffc63f78-4e29-49c3-b2e1-cc64768b3f12'), max_length=37, primary_key=True, serialize=False),
        ),
    ]
