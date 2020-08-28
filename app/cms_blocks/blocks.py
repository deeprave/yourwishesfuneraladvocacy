# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


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

    image = ImageChooserBlock(blank=True, null=True,
                              help_text='Image the automagically cropped to 786px by 552px')
    title = blocks.CharBlock(required=False, blank=True, null=True, max_length=60,
                             help_text='Max length of 60 characters.')
    text = blocks.RichTextBlock(blank=True, required=False, features=RICHTEXTBLOCK_FEATURES,
                                help_text='Description for this item')
    link = Link(required=False)

    class Meta:
        template = "blocks/image_and_text_block.html"
        icon = "image"
        label = "Image & Text"


class CallToActionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, blank=True, null=True, max_length=60,
                             help_text='Max length of 60 characters, optional')
    text = blocks.RichTextBlock(required=False, blank=True, features=RICHTEXTBLOCK_FEATURES,
                                help_text='Call to action text, optional (max=200)')
    link = Link()

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