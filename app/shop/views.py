from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView

from .cart import Cart, CartOrder
from .forms import CartItemForm, OrderForm
from .models import Product, Category, Order


__all__ = (
    'ProductListView',
    'ProductDetailView',
    'cart_additem',
    'cart_removeitem',
    'cart_clear'
)


class CategoryMixin:

    # noinspection PyUnresolvedReferences
    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductListView(CategoryMixin, ListView):
    model = Product
    context_object_name = 'products'

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = self.category
        return context

    # noinspection PyAttributeOutsideInit
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


class ProductDetailView(CategoryMixin, DetailView):
    model = Product
    context_object_name = 'product'

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        return self.get_queryset().filter(**{self.get_slug_field(): slug}).get()

    def get(self, request, slug=None, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Product.DoesNotExist:
            messages.warning(request, f"Unknown product '{slug}'")
        return redirect(to='products')


class CartView(CategoryMixin, TemplateView):
    template_name = 'shop/cart.html'


@require_POST
def cart_additem(request):
    form = CartItemForm(request.POST)
    if form.is_valid():
        product_code = form.cleaned_data['product_code']
        product_quantity = form.cleaned_data.get('product_quantity', 1) or 1
        cart = Cart(request)
        product = get_object_or_404(Product, code=product_code)
        cart.add(product, quantity=product_quantity)
        messages.info(request, f'{product.code} {product.title} ({product_quantity}) added to cart.')
    else:
        messages.error(request, form.errors)
    return_url = request.POST.get('next', reverse('products'))
    return redirect(to=return_url)


@require_POST
def cart_removeitem(request):
    form = CartItemForm(request.POST)
    if form.is_valid():
        product_code, product_quantity = form.cleaned_data['product_code'], form.cleaned_data['product_quantity']
        cart = Cart(request)
        product = get_object_or_404(Product, code=product_code)
        cart.remove(product, quantity=product_quantity)
        messages.info(request, f'{product.code} {product.title} ({product_quantity}) removed from cart.')
    else:
        messages.error(request, form.errors)
    return_url = request.POST.get('next', reverse('cart'))
    return redirect(to=return_url)


@require_POST
def cart_clear(request):
    Cart(request).clear()
    messages.info(request, 'All products removed from your shopping cart.')
    return_url = request.POST.get('next', reverse('products'))
    return redirect(to=return_url)


@require_POST
def create_order(request):
    cart = Cart(request)
    if len(cart) < 1:
        messages.error(request, 'There are no products in your shopping cart.')
        return_url = request.POST.get('next', reverse('products'))
        return redirect(to=return_url)
    # redirect to order confirmation
    return redirect(to='order')


class OrderView(CreateView):
    template_name = 'shop/order.html'
    form_class = OrderForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cart'] = self.cart
        return kwargs

    def get_success_url(self):
        messages.info(self.request, 'Your order has been successfully created.')
        cart = Cart(self.request)
        cart.clear()
        return reverse('payment', args=(self.object.id,))

    def get(self, request, *args, **kwargs):
        self.cart = Cart(request)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.cart = Cart(request)
        return super().post(request, *args, **kwargs)


class PaymentView(DetailView):
    template_name = 'shop/payment.html'
    context_object_name = 'order'
    model = Order

    def get_queryset(self):
        return Order.objects.get(pk=self.order.order_id).select_related('order_items')

    def get(self, request, orderid=None):
        self.order = CartOrder(request)
        return super().get(request, orderid=orderid)
