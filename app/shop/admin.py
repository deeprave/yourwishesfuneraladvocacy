from django.contrib import admin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup

from .models import Category, Product, Order, OrderItem


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


# Register your models here.
class ProductCategoryAdmin(ModelAdmin):
    model = Category
    menu_label = 'Categories'
    menu_icon = 'folder-open-inverse'
    menu_order = 0
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('name', 'slug')
    search_fields = ('code', 'slug')


class ProductsAdmin(ModelAdmin):
    model = Product
    menu_label = 'Products'
    menu_icon = 'tag'
    menu_order = 1
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('code', 'available', 'title', 'slug', 'detail')
    search_fields = ('code', 'title', 'slug', 'detail')


# noinspection PyMethodMayBeStatic
class OrdersAdmin(ModelAdmin):
    model = Order
    menu_label = 'Orders'
    menu_icon = 'form'
    menu_order = 3
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('id', 'created', 'status', 'paid', 'name', 'email', 'total_items', 'total_price')
    search_fields = ('first_name', 'last_name', 'email')


class ShopGroup(ModelAdminGroup):
    menu_label = 'Shop'
    menu_icon = 'pick'
    menu_order = 500
    items = (ProductCategoryAdmin, ProductsAdmin, OrdersAdmin)


modeladmin_register(ShopGroup)
