# -*- coding: utf-8 -*-
from wagtail.core import blocks
from wagtail.images import blocks as img_blocks


__all__ = (
    'ImageBlock',
)


class ImageBlock(blocks.StructBlock):
    image = img_blocks.ImageChooserBlock(required=False)

    class Meta:
        template = 'cms/blocks/image.html'
