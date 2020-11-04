from django.contrib import admin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup

from .models import Category, Product

@admin.register(Category)
class AdminProductCategory(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ('code', 'available', 'title', 'slug', 'detail')
    search_fields = ('code', 'title', 'slug', 'detail')


# Register your models here.
class ProductCategoryAdmin(ModelAdmin):
    model = Category
    menu_label = 'Categories'
    menu_icon = 'folder-open-inverse'
    menu_order = 0
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('name', 'slug')
    search_fields =('code', 'slug')


class ProductsAdmin(ModelAdmin):
    model = Product
    menu_label = 'Products'
    menu_icon = 'tag'
    menu_order = 1
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('code', 'available', 'title', 'slug', 'detail')
    search_fields = ('code', 'title', 'slug', 'detail')


class ProductsGroup(ModelAdminGroup):
    menu_label = 'Products'
    menu_icon = 'pick'
    menu_order = 500
    items = (ProductCategoryAdmin, ProductsAdmin)


modeladmin_register(ProductsGroup)
