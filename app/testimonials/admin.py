from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Testimonial

@modeladmin_register
class TestimonialAdmin(ModelAdmin):
    model = Testimonial
    menu_label = 'Testimonials'
    menu_icon = 'placeholder'
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('quote', 'attribution')
    search_fields =('quote', 'attribution')

