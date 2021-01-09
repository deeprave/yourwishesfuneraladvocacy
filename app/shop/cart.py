# -*- coding: utf-8 -*-
from django.conf import settings
from wagtail.core.models import Site

from .models import Product, ShopSettings, Order, OrderStatus


class Cart:
    """
    Shopping cart container
    """

    def __init__(self, request):
        self.session = request.session
        self.session['shipping'] = self.shop_settings
        self._cart = None

    @property
    def shop_settings(self):
        shop_settings = ShopSettings.for_site(Site.objects.get(is_default_site=True))
        return {
            'charge': shop_settings.shipping_charge,
            'bulk_charge': shop_settings.bulk_shipping_charge,
            'quantity': shop_settings.bulk_quantity,
            'tax_rate': shop_settings.tax_rate,
        }

    @property
    def cart(self):
        if self._cart is None:
            self._cart = self.session.get(settings.CART_SESSION_ID, {})
            if not self._cart:
                self.session[settings.CART_SESSION_ID] = self._cart
        return self._cart

    def add(self, product: Product, quantity=1, update_quantity=False):
        if quantity >= 0:
            if product.code not in self.cart:
                self.cart[product.code] = dict(quantity=0, price=product.price)
            if update_quantity:
                self.cart[product.code]['quantity'] = quantity
            else:
                self.cart[product.code]['quantity'] += quantity
            self.save()

    def remove(self, product, quantity=None):
        if product.code in self.cart:
            if quantity is None or quantity >= self.cart[product.code]['quantity']:
                del self.cart[product.code]
            else:
                self.cart[product.code]['quantity'] -= quantity
            self.save()

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self._cart = None
            self.save()

    @property
    def total_price(self):
        return sum(item['price'] * item['quantity'] for item in self.cart.values()) + self.shipping_price

    @property
    def total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def shipping(self):
        for item in self:
            if item['product'].shipping:
                return True
        return False

    @property
    def tax_rate(self):
        return self.session['shipping']['tax_rate']

    @property
    def shipping_price(self):
        """wagtail specific basesetting"""
        total_quantity = self.total_quantity
        shipping = self.session['shipping']
        return shipping['charge'] if total_quantity < shipping['quantity'] else shipping['bulk_charge']

    @property
    def modified(self):
        return self.session.modified

    @property
    def length(self):
        return len(self.cart.keys())

    def save(self):
        self.session.modified = True

    def __iter__(self):
        cart = self.cart.copy()
        for product in Product.objects.filter(code__in=list(cart.keys())):
            cart[product.code]['product'] = product
        for item in cart.values():
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return len(self.cart.keys())


class CartOrder:

    def __init__(self, request, order_id=None):
        self.session = request.session
        if order_id:
            self.session['order_id'] = order_id
            self.session.modified = True
        self._order = None

    @property
    def order_id(self) -> int:
        return self.session['order_id']

    @property
    def order(self) -> Order:
        if self._order is None:
            self._order = Order.objects.get(pk=self.order_id)
        return self._order

    @property
    def order_status(self) -> OrderStatus:
        return OrderStatus.value_Of(self.order.order_status)

    @property
    def paid_status(self) -> bool:
        return self.order.paid_status

    @property
    def total_price(self) -> float:
        return self.order.total_price

    @property
    def total_items(self) -> float:
        return self.order.total_items
