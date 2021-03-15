# -*- coding: utf-8 -*-
import re
from datetime import timedelta, datetime
from dateutil.tz import tzlocal
from typing import Union

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.snippets.models import register_snippet

from shop.utils import convert_to_str


class Category(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    slug = models.SlugField(max_length=64, unique=True, editable=True)

    def get_absolute_url(self):
        return reverse('shop:product-category', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Product(models.Model):
    RX_PRODUCT_CODE = re.compile(r'^[A-Za-z0-9\-]+$')

    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE,)
    code = models.CharField(max_length=16, unique=True, validators=[RegexValidator(regex=RX_PRODUCT_CODE)],
                            help_text='A unique identifier for this product. Letters, digits, dashes allowed')
    title = models.CharField(max_length=256, help_text='A brief title for this product')
    slug = models.SlugField(max_length=128, unique=True, editable=False,
                            help_text='Unique string that identifies this product in URLs')
    detail = models.TextField(help_text='An optional description of this product', blank=True, default='')
    image = models.ImageField(upload_to='products/%Y%m', blank=True, help_text='An optional image of this product')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Unit price for this product')
    available = models.BooleanField(default=True, help_text='Is this product available?')
    shipping = models.BooleanField(default=True, help_text='Is there a shipping charge for this product?')

    def created(self):
        return self.dt_created.replace(microsecond=0, tzinfo=tzlocal()).isoformat(sep=' ')

    def updated(self):
        return self.dt_updated.replace(microsecond=0, tzinfo=tzlocal()).isoformat(sep=' ')

    def get_absolute_url(self):
        return reverse('product-detail', args=(self.slug,))

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ('code',)


register_snippet(Product)


class OrderStatus(models.IntegerChoices):
    UNKNOWN = -2, _('Unknown')
    CANCELLED = -1, _('Cancelled')
    NEW_ORDER = 0, _('New Order')
    READY = 1, _('Ready for Payment')
    PAYMENT_ACCEPT = 2, _('Accepting Payment')
    PAYMENT_PROCESSING = 3, _('Processing Payment')
    PAYMENT_COMPLETE = 4, _('Payment Completed')
    DISPATCHED = 5, _('Dispatched')
    COMPLETED = 6, _('Completed')

    @classmethod
    def value_of(cls, v: int):
        for s in cls:
            if s.value == v:
                return s
        return cls.UNKNOWN


class Order(models.Model):

    TIMEOUT_PROCESSING = timedelta(minutes=5)
    TIMEOUT_PAYMENT = timedelta(hours=1)

    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)

    first_name = models.CharField(_('First Name'), max_length=60)
    last_name = models.CharField(_('Last Name'), max_length=60)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=40, blank=True)
    address = models.TextField(_('Address'))
    city = models.CharField(_('City'), max_length=100)
    postal_code = models.CharField(_('Postal Code'), max_length=20)

    order_status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.NEW_ORDER)
    paid_status = models.BooleanField(default=False)

    # total_price includes both of the following components
    shipping = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_absolute_url(self):
        return reverse('order-detail', args=(self.id,))

    def __str__(self):
        return f'Order #{self.id}'

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def paid(self):
        return 'Paid' if self.paid_status else 'Unpaid'

    @property
    def status(self):
        return f'{OrderStatus.value_of(self.get_status()).label}'

    @property
    def can_accept_payment(self):
        return self.get_status() in (OrderStatus.NEW_ORDER, OrderStatus.READY)

    @property
    def paid_or_cancelled(self):
        return self.get_status() in (OrderStatus.PAYMENT_PROCESSING, OrderStatus.PAYMENT_COMPLETE, OrderStatus.CANCELLED)

    def created(self):
        return self.dt_created.replace(microsecond=0, tzinfo=tzlocal()).isoformat(sep=' ')

    def updated(self):
        return self.dt_updated.replace(microsecond=0, tzinfo=tzlocal()).isoformat(sep=' ')

    def get_status(self):
        # fix up some timeod out
        now = datetime.now(tz=tzlocal())
        if self.order_status == OrderStatus.PAYMENT_ACCEPT:
            # accept payment timeout ... reset order
            expires_at = self.dt_updated + self.TIMEOUT_PROCESSING
            if now > expires_at:
                self.set_status(OrderStatus.READY, timestamp=now)
        return self.order_status

    def set_status(self, status: OrderStatus, timestamp: Union[None, datetime]=None):
        updated_at = timestamp if timestamp else datetime.now(tz=tzlocal())
        self.dt_updated = updated_at
        self.order_status = status
        self.save()

    @property
    def total_items(self):
        return self.items.count()

    def save(self, **kwargs):
        creating = self.id is None
        cart = kwargs.pop('cart', None)
        if creating and cart:
            # fill some additional values from cart
            self.shipping = cart.shipping_price if cart.shipping else 0.0
            self.total_price = cart.total_price
            self.tax = self.total_price / (cart.tax_rate + 1) if cart.tax_rate else 0.0
        super().save(**kwargs)
        # create the items
        if creating and cart:
            for item in cart:
                product = item['product']
                price = item['price']
                quantity = int(item['quantity'])
                OrderItem.objects.create(order=self, product=product, price=price, quantity=quantity)

    class Meta:
        ordering = ('id',)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{id}'

    @property
    def price_total(self):
        return self.price * self.quantity

    class Meta:
        ordering = ('-order', 'id',)


class Action(models.IntegerChoices):
    UNKNOWN = -1, ('unknown')
    CREATED = 0, _('created')
    ACCEPTED = 1, _('accepted')
    CANCELLED = 2, _('cancelled')
    CONFIRMED = 3, _('confirmed')

    @classmethod
    def value_of(cls, v: int):
        for s in cls:
            if s.value == v:
                return s
        return cls.UNKNOWN


class StripePayment(models.Model):
    """
    This is a simple log of stripe payment transactions
    """
    dt_created = models.DateTimeField(editable=False, auto_now_add=True,
                                      help_text='date and time created')
    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE, help_text='Related order')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Total amount paid')
    session_id = models.TextField(help_text='Transaction session id')
    milestone = models.IntegerField(choices=Action.choices, help_text='Action for this esssion')
    session_data = models.TextField(blank=True, null=True, help_text='Verbose session data')

    @classmethod
    def record_action(self, order, session_id, milestone: Action, amount=None, session_data=None):
        session_data = convert_to_str(session_data)
        return StripePayment.objects.create(order=order, session_id=session_id,
                                            amount=amount or order.total_price,
                                            milestone=milestone, session_data=session_data)

    @property
    def action(self):
        return Action.value_of(self.milestone).label

    def created(self):
        return self.dt_created.replace(microsecond=0, tzinfo=tzlocal()).isoformat(sep=' ')

    def __str__(self):
        return f"Payment {self.created} {self.record_action}"

    class Meta:
        ordering = ('-dt_created', 'milestone')


@register_setting
class ShopSettings(BaseSetting):
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bulk_quantity = models.PositiveIntegerField(default=100, null=True)
    bulk_shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    panels = [
        FieldPanel("shipping_charge"),
        FieldPanel("bulk_quantity"),
        FieldPanel("bulk_shipping_charge"),
        FieldPanel("tax_rate"),
    ]

    def save(self, *args, **kwargs):
        key = make_template_fragment_key("shop_shipping_settings")
        cache.delete(key)
        return super().save(*args, **kwargs)
