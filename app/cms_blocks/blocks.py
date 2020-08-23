# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
from wagtail.core.blocks import PageChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


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
    link_text = blocks.CharBlock(max_length=50, default='More details')
    internal_page = PageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False)

    def clean(self, value):
        errors = {}
        internal_page = value.get('internal_page')
        external_link = value.get('external_link')
        error_message = 'You must enter an external link OR select an internal page'
        if (not internal_page and not external_link) or (internal_page and external_link):
            errors['internal_page'] = ErrorList([error_message])
            errors['external_link'] = ErrorList([error_message])
        if errors:
            raise ValidationError('Link validation error', params=errors)
        return super().clean(value)

    class Meta:
        value_class = LinkValue


class Card(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100, help_text='Bold title text for this card (len=100)')
    text = blocks.TextBlock(max_length=255, required=False, help_text='Optional text for this card (length=255)')
    image = ImageChooserBlock(help_text="Image - auto-cropped 570x370px")
    link = Link(blank=True, help_text='Enter a link or select a page')


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
    image_alignment = RadioSelectBlock(
        choices=(("left", "Image to the left"), ("right", "Image to the right"),),
        default='left',
        help_text='Image on the left with text on the right. Or image on the right with text on the left.'
    )
    title = blocks.CharBlock(max_length=60,
                             help_text='Max length of 60 characters.')
    text = blocks.CharBlock(max_length=140, required=False,
                            help_text='Description for this card (optional)')
    link = Link()

    class Meta:
        template = "blocks/image_and_text_block.html"
        icon = "image"
        label = "Image & Text"


class CallToActionBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200, help_text='Call to action text (max=200)')
    link = Link()

    class Meta:
        template = "blocks/call_to_action_block.html"
        icon = "plus"
        label = "Call to Action"


class CustomTableBlock(TableBlock):

    class Meta:
        template = 'blocks/custom_table_block.html'
        label = 'Pricing Table'
        icon = 'table'
        help_text = 'Price table'


RICHTEXTBLOCK_FEATURES = [
    'h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'hr', 'document-link', 'image', 'embed',
    'code', 'blockquote', 'superscript', 'subscript', 'strikethrough'
]


class RichTextWithTitleBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=50)
    content = blocks.RichTextBlock(features=RICHTEXTBLOCK_FEATURES)

    class Meta:
        template = 'blocks/simple_richtext_block.html'


class TestimonialChooserBlock(SnippetChooserBlock):

    def __init__(self, **kwargs):
        super().__init__('testimonials.Testimonial', **kwargs)

    class Meta:
        template = 'blocks/testimonial_block.html'


class LargeImageChooserBlock(ImageChooserBlock):

    class Meta:
        template = 'blocks/large_image_block.html'
