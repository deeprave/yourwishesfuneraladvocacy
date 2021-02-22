from django.contrib import admin
from django.utils.html import format_html
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup
from wagtail.images.edit_handlers import ImageChooserPanel

from .models import Category, Product, Order, OrderItem, StripePayment


@admin.register(Category)
class AdminProductCategory(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ('code', 'available', 'title', 'slug', 'detail')
    search_fields = ('code', 'title', 'slug', 'detail')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)


# noinspection PyMethodMayBeStatic
@admin.register(Order)
class AdminOrder(admin.ModelAdmin):
    list_display = ('id', 'created', 'status', 'first_name', 'last_name',
                    'email', 'address', 'postal_code', 'city', 'updated',)
    search_fields = ('first_name', 'last_name', 'email', 'address', 'city',)
    list_filter = ('paid_status', 'order_status',)
    inlines = (OrderItemInline,)


@admin.register(StripePayment)
class AdminStripePayment(admin.ModelAdmin):
    list_display = ('id', 'created', 'order_url', 'milestone', 'session_id')

    def order_url(self, obj):
        order = obj.order
        return format_html(f'<a href="{order.get_absolute_url()}" alt="{order}">{order}</a>')


class ProductCategoryAdmin(ModelAdmin):
    model = Category
    menu_label = 'Categories'
    menu_icon = 'folder-open-inverse'
    menu_order = 0
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('slug')
        ])
    ]

class ProductsAdmin(ModelAdmin):
    model = Product
    menu_label = 'Products'
    menu_icon = 'tag'
    menu_order = 1
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('code', 'available', 'title', 'slug', 'detail')
    search_fields = ('code', 'title', 'slug', 'detail')

    panels = [
        MultiFieldPanel([
            FieldPanel('category'),
            FieldPanel('code'),
            FieldPanel('title'),
            FieldPanel('detail'),
            FieldPanel('image'),
            FieldPanel('price'),
            FieldPanel('available'),
            FieldPanel('shipping'),
        ])
    ]


# noinspection PyMethodMayBeStatic
class OrdersAdmin(ModelAdmin):
    model = Order
    menu_label = 'Orders'
    menu_icon = 'form'
    menu_order = 3
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('id', 'created', 'url', 'status', 'paid', 'name', 'email', 'total_items', 'total_price')
    search_fields = ('first_name', 'last_name', 'email')

    def url(self, order):
        return format_html(f'<a href="{order.get_absolute_url()}" alt="{order}">{order}</a>')

class StripePaymentAdmin(ModelAdmin):
    model = StripePayment
    menu_label = 'Payments'
    menu_icon = 'success'
    menu_order = 4
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('id', 'created', 'order_url', 'action', 'session_id')
    search_fields = ('dt_created', 'milestone', 'order__id')

    def order_url(self, obj):
        order = obj.order
        return format_html(f'<a href="{order.get_absolute_url()}" alt="{order}">{order}</a>')


class ShopGroup(ModelAdminGroup):
    menu_label = 'Shop'
    menu_icon = 'pick'
    menu_order = 500
    items = (ProductCategoryAdmin, ProductsAdmin, OrdersAdmin, StripePaymentAdmin)


modeladmin_register(ShopGroup)

