# Generated by Django 5.1.6 on 2025-02-14 10:04

import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_api_tokens_apisettings_dmppage_dmpsearchpage_and_more'),
        ('wagtailimages', '0027_image_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dmpviewpage',
            name='intro',
        ),
        migrations.RemoveField(
            model_name='footersettings',
            name='github_icon',
        ),
        migrations.RemoveField(
            model_name='footersettings',
            name='github_url',
        ),
        migrations.AddField(
            model_name='apisettings',
            name='api_token',
            field=models.CharField(blank=True, help_text='Optional token for authenticating API requests', max_length=255, verbose_name='API Token'),
        ),
        migrations.AlterField(
            model_name='apisettings',
            name='elab_base_url',
            field=models.URLField(blank=True, help_text='Base URL for the eLab API', verbose_name='eLab Base URL'),
        ),
        migrations.AlterField(
            model_name='apisettings',
            name='jenkins_base_url',
            field=models.URLField(blank=True, help_text='Base URL for the Jenkins API', verbose_name='Jenkins Base URL'),
        ),
        migrations.AlterField(
            model_name='footersettings',
            name='footer_text',
            field=models.TextField(blank=True, help_text='Text displayed in the website footer', verbose_name='Footer Text'),
        ),
        migrations.AlterField(
            model_name='headersettings',
            name='header_text',
            field=wagtail.fields.RichTextField(blank=True, help_text='Text displayed in the website header', verbose_name='Header Text'),
        ),
        migrations.AlterField(
            model_name='headersettings',
            name='prp_icon',
            field=models.ForeignKey(blank=True, help_text='Icon displayed in the header', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Header Icon'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.fields.RichTextField(blank=True, help_text='Main body content of the home page, supports rich text formatting.'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='intro',
            field=models.CharField(default='', help_text='Short introductory text displayed on the home page.', max_length=250),
        ),
        migrations.AlterField(
            model_name='samplepage',
            name='thankyou_page_title',
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]
