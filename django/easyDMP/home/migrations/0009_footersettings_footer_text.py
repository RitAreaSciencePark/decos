# Generated by Django 5.0.6 on 2024-06-27 07:21

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_rename_navigationsettings_footersettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='footersettings',
            name='footer_text',
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]
