# -*- coding: utf-8 -*-
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase, Tag as TaggitTag
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel, InlinePanel
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from django.db import models
from cms_blocks import blocks as cmsblocks


__all__ = (
    'CMSPage',
)


class PageTag(TaggedItemBase):
    content_object = ParentalKey('cms.CMSPage', related_name='page_tags')


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True


class AbstractCMSPage(Page):
    """
    Abstract base page for the CMS
    """
    tags = ClusterTaggableManager(through='cms.PageTag', blank=True,
                                  help_text='Tags used to search for this page (optional)')
    display_title = models.BooleanField(default=True)

    content_panels = [
        FieldPanel('title'),
        FieldPanel('tags'),
    ]

    class Meta:
        abstract = True


AbstractCMSPage.promote_panels = [
    MultiFieldPanel(Page.promote_panels + [FieldPanel('display_title')], "Common page configuration"),
]


class CMSPage(AbstractCMSPage):
    parent_page_types = ['wagtailcore.page', 'cms.CMSPage']

    body = StreamField([
        ('title',           cmsblocks.TitleBlock()),
        ('cards',           cmsblocks.CardsBlock()),
        ('image_and_text',  cmsblocks.ImageAndTextBlock()),
        ('cta',             cmsblocks.CallToActionBlock()),
        ('table',           cmsblocks.CustomTableBlock()),
        ('richtext',        cmsblocks.RichTextWithTitleBlock()),
        ('testimonial',     cmsblocks.TestimonialChooserBlock(
            help_text='Select testimonial'
        )),
        ('large_image',     cmsblocks.LargeImageChooserBlock(
            help_text='A large image - cropped to 1200x775',
        )),
        ('new_section',     cmsblocks.NewSectionBlock(
            help_text='Insert a horizontal rule'
        )),
    ], blank=True, null=True)

    content_panels = AbstractCMSPage.content_panels + [
        MultiFieldPanel([
                InlinePanel('carousel_images', max_num=12, min_num=0, label='Carousel Image')
            ], heading='Carousel Images'
        ),
        StreamFieldPanel('body')
    ]

    class Meta:
        verbose_name = 'CMS Page'
        verbose_name_plural = 'CMS Pages'


class CarouselImage(Orderable):
    RICHTEXTBLOCK_FEATURES = [
        'bold', 'italic', 'ol', 'ul'
    ]

    parent_pg = ParentalKey('cms.CMSPage', related_name='carousel_images')
    # noinspection PyUnresolvedReferences
    carousel_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name='+')
    carousel_title = models.CharField(blank=True, null=True, max_length=120,
                                      help_text='Display title, optional (max len=120)')
    carousel_content = RichTextField(features=RICHTEXTBLOCK_FEATURES, null=True, blank=True)
    carousel_attribution = models.CharField(blank=True, null=True, max_length=120,
                                            help_text='Display title, optional (max len=120)')
    carousel_interval = models.IntegerField(blank=False, null=False, default=12000,
                                            help_text='Keep visible for time in milliseconds')

    panels = [
        ImageChooserPanel('carousel_image'),
        FieldPanel('carousel_title'),
        FieldPanel('carousel_content'),
        FieldPanel('carousel_attribution'),
        FieldPanel('carousel_interval')
    ]
