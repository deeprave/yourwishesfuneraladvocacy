# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


__all__ = (
    'Link',
    'CardsBlock',
    'RadioSelectBlock',
    'ImageAndTextBlock',
    'CallToActionBlock',
    'CustomTableBlock',
    'RichTextWithTitleBlock',
    'TestimonialChooserBlock',
    'LargeImageChooserBlock',
    'NewSectionBlock',
)

RICHTEXTBLOCK_FEATURES = [
    'h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'hr', 'document-link', 'image', 'embed',
    'code', 'blockquote', 'superscript', 'subscript', 'strikethrough'
]


class TitleBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, help_text='Title text to display')

    class Meta:
        template = "blocks/title_block.html"
        icon = "edit"
        label = "Title"
        help_text = "Centered text to display on the page"


class LinkValue(blocks.StructValue):

    def url(self) -> str:
        internal_page = self.get('internal_page')
        external_link = self.get('external_link')
        return internal_page if internal_page else external_link if external_link else ''


class Link(blocks.StructBlock):
    link_text = blocks.CharBlock(required=False, blank=True, max_length=50, default='More details')
    internal_page = PageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False)
    required = True

    def __init__(self, local_blocks=None, **kwargs):
        self.required = kwargs.pop('required', self.required)
        super().__init__(local_blocks, **kwargs)

    def clean(self, value):
        errors = {}
        internal_page = value.get('internal_page')
        external_link = value.get('external_link')
        error_message = 'You must enter an external link OR select an internal page'
        if (not internal_page and not external_link and self.required) or (internal_page and external_link):
            errors['internal_page'] = ErrorList([error_message])
            errors['external_link'] = ErrorList([error_message])
        if errors:
            raise ValidationError('Link validation error', params=errors)
        return super().clean(value)

    class Meta:
        value_class = LinkValue


class Card(blocks.StructBlock):
    title = blocks.CharBlock(blank=True, null=True, required=False, max_length=255,
                             help_text='Bold title text for this card (len=255)')
    text = blocks.RichTextBlock(blank=True, null=True, required=False,
                                help_text='Optional text for this card')
    image = ImageChooserBlock(required=False, help_text="Image - auto-cropped 570x370px")
    link = Link(required=False, help_text='Enter a link or select a page')


class CardsBlock(blocks.StructBlock):
    cards = blocks.ListBlock(Card())

    class Meta:
        template = "blocks/cards_block.html"
        icon = "image"
        label = "Cards"


class RadioSelectBlock(blocks.ChoiceBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field.widget = forms.RadioSelect(choices=self.field.widget.choices)


class ImageAndTextBlock(blocks.StructBlock):

    image = ImageChooserBlock(blank=True, null=True)
    image_alignment = RadioSelectBlock(
        choices=(
            ("full", "Full width centered"),
            ("left", "Image to the left"),
            ("right", "Image to the right"),
        ),
        default='full',
        help_text='Full image - text below, Image left - text right, or image right - text left.'
    )
    image_size = RadioSelectBlock(
        choices=(
            ('standard',  'Standard 786x552'),
            ('landscape', 'Landscape 786x1104'),
            ('portrait',  'Portrait 786x300'),
        ),
        default='standard',
        help_text='Layout - match with picture dimensions'
        )
    title = blocks.CharBlock(required=False, blank=True, null=True, max_length=60,
                             help_text='Max length of 60 characters.')
    text = blocks.RichTextBlock(blank=True, required=False, features=RICHTEXTBLOCK_FEATURES,
                                help_text='Description for this item')
    link = Link(required=False, blank=True, null=True)

    class Meta:
        template = "blocks/image_and_text_block.html"
        icon = "image"
        label = "Image & Text"


class CallToActionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, blank=True, null=True, max_length=60,
                             help_text='Max length of 60 characters, optional')
    text = blocks.RichTextBlock(required=False, blank=True, features=RICHTEXTBLOCK_FEATURES,
                                help_text='Call to action text, optional (max=200)')
    link = Link(required=False, blank=True, null=True)

    class Meta:
        template = "blocks/call_to_action_block.html"
        icon = "plus"
        label = "Call to Action"


class CustomTableBlock(TableBlock):

    class Meta:
        template = 'blocks/custom_table_block.html'
        label = 'Table'
        icon = 'table'
        help_text = 'Tabular data'


class RichTextWithTitleBlock(blocks.StructBlock):
    title = blocks.CharBlock(blank=True, null=True, required=False, max_length=120,
                             help_text='Display title, optional (max len=120)')
    content = blocks.RichTextBlock(features=RICHTEXTBLOCK_FEATURES,
                                   help_text='Rich text block, required')

    class Meta:
        template = 'blocks/simple_richtext_block.html'
        label = 'RichText with Title'
        icon = 'doc-empty-inverse'


class TestimonialChooserBlock(SnippetChooserBlock):

    def __init__(self, **kwargs):
        super().__init__('testimonials.Testimonial', **kwargs)

    class Meta:
        template = 'blocks/testimonial_block.html'
        icon = 'tick-inverse'
        label = 'Testimonial'


class LargeImageChooserBlock(ImageChooserBlock):

    class Meta:
        template = 'blocks/large_image_block.html'


class NewSectionBlock(blocks.StructBlock):

    class Meta:
        template = 'blocks/new_section.html'
        icon = 'horizontalrule'
        label = 'Start new sectiom'
