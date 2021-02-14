# -*- coding: utf-8 -*-
from django.utils.functional import SimpleLazyObject

from .cart import Cart


def cart(request):

    def _get_cart():
        return Cart(request)

    return {
        'cart': SimpleLazyObject(_get_cart)
    }
