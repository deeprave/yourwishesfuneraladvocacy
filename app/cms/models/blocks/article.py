# -*- coding: utf-8 -*-
from wagtail.core import blocks
from wagtail.images import blocks as image_blocks


__all__ = (
    'ArticleBlock',
)


class ArticleBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, help_text='Article heading (optional)')
    image = image_blocks.ImageChooserBlock(required=False, help_text='Image (optional)')
    article = blocks.RichTextBlock(help_text='Article Text')
    url = blocks.URLBlock(required=False, help_text='Related link (optional)')

    class Meta:
        icon = "dock-full-inverse"
        template = 'cms/blocks/_article.html'
