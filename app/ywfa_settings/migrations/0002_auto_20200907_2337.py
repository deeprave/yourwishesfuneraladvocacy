# Generated by Django 3.1.1 on 2020-09-07 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ywfa_settings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactsettings',
            name='email_address',
        ),
        migrations.RemoveField(
            model_name='contactsettings',
            name='email_display_text',
        ),
        migrations.RemoveField(
            model_name='contactsettings',
            name='phone_display_text',
        ),
        migrations.RemoveField(
            model_name='contactsettings',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='contactsettings',
            name='book_button_link',
            field=models.URLField(blank=True, default=None, help_text='Enter the URL to make a booking', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='contactsettings',
            name='book_button_text',
            field=models.CharField(blank=True, help_text='Enter the text for make booking', max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='socialmediasettings',
            name='snapchat',
            field=models.URLField(blank=True, help_text='Enter your Snapchat URL'),
        ),
    ]