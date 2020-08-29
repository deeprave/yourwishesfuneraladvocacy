# Generated by Django 3.1 on 2020-08-29 07:33

import cms_blocks.blocks
from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_auto_20200826_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cmspage',
            name='body',
            field=wagtail.core.fields.StreamField([('title', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.CharBlock(help_text='Title text to display', required=True))])), ('cards', wagtail.core.blocks.StructBlock([('cards', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(blank=True, help_text='Bold title text for this card (len=255)', max_length=255, null=True, required=False)), ('text', wagtail.core.blocks.RichTextBlock(blank=True, help_text='Optional text for this card', null=True, required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(help_text='Image - auto-cropped 570x370px', required=False)), ('link', wagtail.core.blocks.StructBlock([('link_text', wagtail.core.blocks.CharBlock(blank=True, default='More details', max_length=50, required=False)), ('internal_page', wagtail.core.blocks.PageChooserBlock(required=False)), ('external_link', wagtail.core.blocks.URLBlock(required=False))], help_text='Enter a link or select a page'))])))])), ('image_and_text', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(blank=True, help_text='Image the automagically cropped to 786px by 552px', null=True)), ('image_alignment', wagtail.core.blocks.ChoiceBlock(choices=[('full', 'Full width centered'), ('left', 'Image to the left'), ('right', 'Image to the right')], help_text='Full image - text below, Image left - text right, or image right - text left.')), ('title', wagtail.core.blocks.CharBlock(blank=True, help_text='Max length of 60 characters.', max_length=60, null=True, required=False)), ('text', wagtail.core.blocks.RichTextBlock(blank=True, features=['h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'hr', 'document-link', 'image', 'embed', 'code', 'blockquote', 'superscript', 'subscript', 'strikethrough'], help_text='Description for this item', required=False)), ('link', wagtail.core.blocks.StructBlock([('link_text', wagtail.core.blocks.CharBlock(blank=True, default='More details', max_length=50, required=False)), ('internal_page', wagtail.core.blocks.PageChooserBlock(required=False)), ('external_link', wagtail.core.blocks.URLBlock(required=False))]))])), ('cta', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(blank=True, help_text='Max length of 60 characters, optional', max_length=60, null=True, required=False)), ('text', wagtail.core.blocks.RichTextBlock(blank=True, features=['h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'hr', 'document-link', 'image', 'embed', 'code', 'blockquote', 'superscript', 'subscript', 'strikethrough'], help_text='Call to action text, optional (max=200)', required=False)), ('link', wagtail.core.blocks.StructBlock([('link_text', wagtail.core.blocks.CharBlock(blank=True, default='More details', max_length=50, required=False)), ('internal_page', wagtail.core.blocks.PageChooserBlock(required=False)), ('external_link', wagtail.core.blocks.URLBlock(required=False))]))])), ('table', cms_blocks.blocks.CustomTableBlock()), ('richtext', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(blank=True, help_text='Display title, optional (max len=120)', max_length=120, null=True, required=False)), ('content', wagtail.core.blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'hr', 'document-link', 'image', 'embed', 'code', 'blockquote', 'superscript', 'subscript', 'strikethrough'], help_text='Rich text block, required'))])), ('testimonial', cms_blocks.blocks.TestimonialChooserBlock(help_text='Select testimonial')), ('large_image', cms_blocks.blocks.LargeImageChooserBlock(help_text='A large image - cropped to 1200x775'))], blank=True, null=True),
        ),
    ]
