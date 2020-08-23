# -*- coding: utf-8 -*-
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase, Tag as TaggitTag
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet

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

    content_panels = [
        FieldPanel('title'),
        FieldPanel('tags'),
    ]
    class Meta:
        abstract = True


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
    ], blank=True, null=True)

    content_panels = AbstractCMSPage.content_panels + [
        StreamFieldPanel('body')
    ]

    class Meta:
        verbose_name = 'CMS Page'
        verbose_name_plural = 'CMS Pages'
