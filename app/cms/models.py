# -*- coding: utf-8 -*-
from taggit.managers import TaggableManager
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images import blocks as images_blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock
from cms_blocks import models as cms_blocks


__all__ = (
    'CMSPage',
)

class Templates:
    RICHTEXT = 'streams/simple_richtext_block.html'
    LARGEIMAGE = 'streams/large_image_block.html'
    TESTIMONIAL = 'streams/testimonial_block.html'


class AbstractCMSPage(Page):
    """
    Abstract base page for the CMS
    """
    tags = TaggableManager(blank=True, help_text='Tags used to search for this page (optional)')

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
    ]

    class Meta:
        abstract = True


class CMSPage(AbstractCMSPage):
    parent_page_types = ['cms.HomePage', 'cms.CMSPage']

    body = StreamField([
        ('title',           cms_blocks.TitleBlock()),
        ('cards',           cms_blocks.CardsBlock()),
        ('image_and_text',  cms_blocks.ImageAndTextBlock()),
        ('cta',             cms_blocks.CallToActionBlock()),
        ('price_table',     cms_blocks.CustomTableBlock()),
        ('richtext',        cms_blocks.RichTextWithTitleBlock()),
        ('testimonial',     SnippetChooserBlock('testimonials.Testimonial', template=Templates.TESTIMONIAL)),
        ('large_image',     images_blocks.ImageChooserBlock(
            help_text='A large image - cropped to 1200x775',
            template=Templates.LARGEIMAGE
        )),
    ], null=True, blank=True)

    content_panels = AbstractCMSPage.content_panels + [
        StreamFieldPanel('body'),
    ]

    class Meta:
        verbose_name = 'CMS Page'
        verbose_name_plural = 'CMS Pages'


class HomePage(CMSPage):
    parent_page_types = ['wagtailcore.page']
