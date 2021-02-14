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
    cart, order = request.session.get(settings.CART_SESSION_ID), request.session.get(settings.ORDER_SESSION_ID)
    context['cart_available'], context['order_available']= cart and len(cart) > 0, order and len(order) > 0
    return context
