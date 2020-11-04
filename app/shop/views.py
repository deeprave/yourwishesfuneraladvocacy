from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView

from .models import Product, Category


__all__ = (
    'ProductListView',
)


class ProductListView(ListView):
    model = Product
    context_object_name = 'products'

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = self.categories
        context['category'] = self.category
        return context

    def get(self, request, slug=None, *args, **kwargs):
        self.categories = Category.objects.all()
        self.queryset = Product.objects.filter(available=True)
        self.category = None
        if slug:
            try:
                self.category = Category.objects.get(slug=slug)
                self.queryset = self.queryset.filter(category=self.category)
            except Category.DoesNotExist:
                messages.warning(request, f"Unknown category '{slug}'")
        return super().get(request, *args, **kwargs)


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        return self.get_queryset().filter(**{self.get_slug_field(): slug}).get()

    def get(self, request, slug=None, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Product.DoesNotExist:
            messages.warning(request, f"Unknown product '{slug}'")
        return redirect(to='products')


def add_to_cart(request, id: int=0, slug: str=None):
    pass
