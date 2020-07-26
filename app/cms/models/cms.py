# -*- coding: utf-8 -*-
from django.db import models
from taggit.managers import TaggableManager
from wagtail.admin.edit_handlers import FieldPanel, RichTextField
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.images import blocks as image_blocks
from wagtail.images.edit_handlers import ImageChooserPanel

__all__ = (
    'CMSPage',
)


class CMSPage(Page):
    page_title = models.CharField(max_length=255, blank=True, null=True,
                        help_text='Page main title')
    page_image = image_blocks.ImageChooserBlock(required=False,
                        help_text='Page main image (optional)')
    page_link = blocks.URLBlock(required=False, blank=True, null=True,
                        help_text='Page image (optional)')
    page_tags = TaggableManager(blank=True,
                        help_text='Tags for this page')
    page_body = RichTextField(required=False, blank=True, null=False,
                        help_text='Page body')

    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        ImageChooserPanel('page_image'),
        FieldPanel('page_link'),
        FieldPanel('page_tags'),
        FieldPanel('page_body'),
    ]

