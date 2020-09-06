from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting
class ContactSettings(BaseSetting):

    contact_button_text = models.CharField(null=True, blank=True, max_length=32, default="Form",
                                           help_text='Enter the text that will appear on the contact button')
    # noinspection PyUnresolvedReferences
    contact_button_page = models.ForeignKey('wagtailcore.Page', blank=True, null=True, related_name='+',
                                            on_delete=models.SET_NULL,
                                            help_text='Select the contact form page to link')

    call_button_text = models.CharField(null=True, blank=True, max_length=32, default="Call",
                                        help_text='Enter the text that will appear on the call button')
    call_button_number = models.CharField(null=True, blank=True, max_length=32, default=None,
                                          help_text='Enter the number to call')

    email_display_text = models.CharField(null=True, blank=True, max_length=32,
                                          help_text='Enter the email address that will appear for email contact')
    email_address = models.CharField(null=True, blank=True, max_length=32,
                                     help_text='Enter the email address that will be used for email contact')

    phone_display_text = models.CharField(null=True, blank=True, max_length=32,
                                          help_text='Enter the number that will appear for phone contact')
    phone_number = models.CharField(null=True, blank=True, max_length=32,
                                    help_text='Enter the phone number that will be used for phone contact')

    panels = [
        FieldPanel("contact_button_text"),
        PageChooserPanel('contact_button_page'),
        FieldPanel("call_button_text"),
        FieldPanel("call_button_number"),
    ]

    def save(self, *args, **kwargs):
        key = make_template_fragment_key("footer_contact_settings")
        cache.delete(key)
        return super().save(*args, **kwargs)


@register_setting
class SocialMediaSettings(BaseSetting):

    facebook = models.URLField(blank=True, help_text='Enter your Facebook URL')
    linkedin = models.URLField(blank=True, help_text='Enter your LinkedIn URL')
    twitter = models.URLField(blank=True, help_text='Enter your Twitter URL')
    youtube = models.URLField(blank=True, help_text='Enter your YouTube URL')
    instagram = models.URLField(blank=True, help_text='Enter your Instagram URL')

    panels = [
        FieldPanel("facebook"),
        FieldPanel("linkedin"),
        FieldPanel("twitter"),
        FieldPanel("youtube"),
        FieldPanel("instagram"),
    ]

    def save(self, *args, **kwargs):
        key = make_template_fragment_key("footer_social_settings")
        cache.delete(key)
        return super().save(*args, **kwargs)
