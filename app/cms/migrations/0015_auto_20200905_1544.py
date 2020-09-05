# Generated by Django 3.1.1 on 2020-09-05 05:44

from django.db import migrations, models
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0014_auto_20200905_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='carouselimage',
            name='carousel_attribution',
            field=models.CharField(blank=True, help_text='Display title, optional (max len=120)', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='carouselimage',
            name='carousel_content',
            field=wagtail.core.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='carouselimage',
            name='carousel_title',
            field=models.CharField(blank=True, help_text='Display title, optional (max len=120)', max_length=120, null=True),
        ),
    ]
