# -*- coding: utf-8 -*-
"""
Shopping cart support
"""
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('shop/partials/_cart.html', takes_context=True)
def cart(context):
    request = context['request']
    cart = request.session.get(settings.CART_SESSION_ID)
    order = request.session.get(settings.ORDER_SESSION_ID)
    for key in ('cart_available', 'order_available'):
        context[key] = False
    if cart and len(cart) > 0:
        context['cart_available'] = True
        context['cart'] = cart
    elif order and len(order) > 0:
        context['order_available'] = cart and len(cart) > 0
        context['order'] = order
    return context
