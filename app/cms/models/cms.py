# -*- coding: utf-8 -*-
from django.db import models
from modelcluster.fields import ParentalKey
from taggit.managers import TaggableManager
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    InlinePanel,
    StreamFieldPanel
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from .blocks.article import ArticleBlock

__all__ = (
    'CMSPage',
    'ArticlePage',
    'ArticleWithCarouselPage',
)


class AbstractCMSPage(Page):
    """
    Abstract base page for the CMS
    """
    subtitle = models.CharField(max_length=255,
                                blank=True,
                                null=True,
                                help_text='The main display title for this page')
    tags = TaggableManager(blank=True,
                           help_text='Tags used to search for this page (optional)')

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('tags'),
    ]

    class Meta:
        abstract = True


class CMSPage(AbstractCMSPage):
    pass


class CMSPageWithBanner(CMSPage):
    """
    Base page container for the CMS
    """
    # noinspection PyUnresolvedReferences
    page_banner = models.ForeignKey('wagtailimages.Image', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="+",
                                    help_text='A banner for the top of the page (optional)')
    page_banner_caption = models.CharField(max_length=255, blank=True, null=True,
                                           help_text='Caption for the banner (optional)')

    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        MultiFieldPanel([
            ImageChooserPanel('page_banner'),
            FieldPanel('page_banner_caption')
        ], heading='Banner Options'),
        FieldPanel('page_tags'),
        FieldPanel('page_body'),
    ]

    class Meta:
        abstract = True


class ArticlePage(CMSPage):
    article = StreamField([
        ('article', ArticleBlock())
    ], blank=True)

    content_panels = CMSPage.content_panels + [
        StreamFieldPanel('article')
    ]

    class Meta:
        verbose_name = "Article Page"
        verbose_name_plural = "Article Pages"


class ArticlePageWithBanner(CMSPageWithBanner):
    article = StreamField([
        ('article', ArticleBlock())
    ], blank=True)

    content_panels = CMSPageWithBanner.content_panels + [
        StreamFieldPanel('article')
    ]

    class Meta:
        verbose_name = "Article Page with Banner"
        verbose_name_plural = "Article Pages with Banner"


class CarouselImages(Orderable):
    """
    Container for carousel images
    """
    page = ParentalKey('ArticleWithCarouselPage', related_name='carousel_images',
                       help_text='Page model on which this carousel appears')
    # noinspection PyUnresolvedReferences
    carousel_image = models.ForeignKey('wagtailimages.Image', null=True, blank=False,
                                       on_delete=models.SET_NULL, related_name='+',
                                       help_text='Image to appear in the carousel')

    panels = [
        ImageChooserPanel('carousel_image'),
    ]


class ArticleWithCarouselPage(ArticlePage):
    """
    Adds carousel images to an article page
    """
    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        MultiFieldPanel([
            InlinePanel('carousel_images', label='Image')
        ], heading='Carousel Images'),
        FieldPanel('page_tags'),
        FieldPanel('page_body'),
        StreamFieldPanel('article'),
    ]

    class Meta:
        verbose_name = "Article Page With Carousel"
        verbose_name_plural = "Article Pages With Carousel"
