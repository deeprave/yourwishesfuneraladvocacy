# Generated by Django 3.1.1 on 2020-09-04 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('cms', '0010_auto_20200905_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carouselimage',
            name='carousel_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
    ]