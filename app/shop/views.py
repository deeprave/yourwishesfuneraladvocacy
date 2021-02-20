from decimal import Decimal
from http import HTTPStatus
from urllib.parse import urlunparse

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, CreateView

import stripe
from stripe.error import SignatureVerificationError

from .cart import Cart
from .forms import CartItemForm, OrderForm
from .models import Product, Category, Order, OrderStatus, StripePayment, Action

__all__ = (
    'ProductListView',
    'ProductDetailView',
    'cart_additem',
    'cart_removeitem',
    'cart_clear'
)

from .utils import get_current_url


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
        self.cart.clear()
        return reverse('payment', args=(self.object.id,))

    def dispatch(self, request, *args, **kwargs):
        self.cart = Cart(request)
        super().dispatch(request, *args, **kwargs)


class OrderDetailView(DetailView):
    template_name = 'shop/order_detail.html'
    model = Order
    context_object_name = 'order'
    pk_url_kwarg = 'orderid'


class PaymentView(DetailView):
    template_name = 'shop/payment.html'
    model = Order
    context_object_name = 'order'
    pk_url_kwarg = 'orderid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def get(self, request, orderid=None, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StripeSuccessView(TemplateView):
    template_name = 'shop/stripe_success.html'

    def get(self, request, order_id, session_id, *args, **kwargs):
        try:
            order: Order = Order.objects.get(pk=order_id)
            if not order.paid_or_cancelled:
                order.set_status(OrderStatus.PAYMENT_PROCESSING)
                StripePayment.record_action(order, session_id, Action.ACCEPTED)
        except Order.DoesNotExist:
            pass    # ignore
        return super().get(request, *args, **kwargs)

class StripeCancelView(TemplateView):
    template_name = 'shop/stripe_cancelled.html'

    def get(self, request, order_id, session_id, *args, **kwargs):
        try:
            order: Order = Order.objects.get(pk=order_id)
            if not order.paid_or_cancelled:
                order.set_status(OrderStatus.CANCELED)
                StripePayment.record_action(order, session_id, Action.CANCELLED)
        except Order.DoesNotExist:
            pass    # ignore
        return super().get(request, *args, **kwargs)


CURRENCY = 'aud'
APPLICATION_PROBLEM_JSON = 'application/problem+json'


def stripe_callback_url(request, responsetype, order_id):
    url = get_current_url(request)
    url[2] = reverse(responsetype, args=(order_id, '{CHECKOUT_SESSION_ID}',))
    return urlunparse(url).replace('%7B', '{').replace('%7D', '}')      # remove urlencoding


def stripe_session(request):
    """ajax handler"""
    if request.method == 'POST':
        # default return
        try:
            orderid, amount = int(request.POST['orderid']), str(request.POST['order_amount'])
            order :Order = Order.objects.get(pk=orderid)
            if Decimal(order.total_price) == Decimal(amount):
                """
                seems in order, create a checkout session
                """
                line_items = [
                    dict(name=item.product.title, quantity=item.quantity, amount=int(item.price*100), currency=CURRENCY)
                    for item in order.items.all()
                ]
                if order.shipping:
                    line_items.append(dict(name='Shipping and handling', quantity=1,
                                           amount=int(order.shipping*100), currency=CURRENCY))
                if order.tax:
                    line_items.append(dict(name='GST', quantity=1,
                                           amount=int(order.tax*100), currency=CURRENCY))
                stripe.api_key = settings.STRIPE_PRIVATE_KEY
                checkout_session = stripe.checkout.Session.create(
                    success_url = stripe_callback_url(request, 'stripe-success', orderid),
                    cancel_url = stripe_callback_url(request, 'stripe-cancel', orderid),
                    payment_method_types = ['card'],
                    mode = 'payment',
                    line_items = line_items
                )
                order.set_status(OrderStatus.PAYMENT_ACCEPT)
                StripePayment.record_action(order, checkout_session['id'], Action.CREATED, session_data=checkout_session)
                return JsonResponse({
                    'status': 'true',
                    'sessionId': checkout_session['id']
                })

        except (Order.DoesNotExist, KeyError):
            pass
        return JsonResponse({
                'status': ''
                          'false',
                'message': 'invalid or obsolete information provided'
            },
            status=HTTPStatus.BAD_REQUEST,
            content_type=APPLICATION_PROBLEM_JSON,
        )
    return JsonResponse({
            'status': 'false',
            'message': f'unsupported method {request.method}'
        },
        status=HTTPStatus.METHOD_NOT_ALLOWED,
        content_type=APPLICATION_PROBLEM_JSON,
    )


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_PRIVATE_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        # Check the received data including signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({
            'status': 'false',
            'message': f'{e}'
        }, status=HTTPStatus.BAD_REQUEST)
    except SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({
            'status': 'false',
            'message': f'{e}'
         }, status=HTTPStatus.NOT_ACCEPTABLE)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return JsonResponse(status=200)
