# -*- coding: utf-8 -*-
from collections import UserDict
from typing import List

import pytest
from django.db.models import Manager

from shop.cart import Cart
from shop.models import Product, Category


class Session(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}
        self.modified = False


class Request:
    def __init__(self):
        self.session = Session()


class Filter:
    def __init__(self, items: List[Product]):
        self.items = items

    def filter(self, **kwargs):
        for _, v in kwargs.items():     # assumes code__in, [array]
            return [product for product in self.items if product.code in v]
        return self.items

class ProductManager(Manager):
    model = Product

    def __init__(self, items):
        self.items = items

    def get_queryset(self):
        return Filter(self.items)


@pytest.fixture
def req():
    return Request()


@pytest.fixture
def products():
    category = Category(name='doesnotmatter')
    return [
        Product(category=category, code='CODE1', title='Product #1', price=15.00),
        Product(category=category, code='CODE2', title='Product #2', price=19.00),
        Product(category=category, code='CODE3', title='Product #3', price=12.00),
        Product(category=category, code='CODE4', title='Product #4', price=5.00),
        Product(category=category, code='CODE5', title='Product #5', price=10.00),
        Product(category=category, code='CODE6', title='Product #6', price=35.00),
    ]

@pytest.fixture
def cart(monkeypatch):
    shop_settings = {
        'charge': 0.00,
        'bulk_charge': 10.00,
        'quantity': 10
    }
    monkeypatch.setattr(Cart, 'shop_settings', shop_settings)
    return Cart(request=Request())

def test_cart(cart):
    assert len(cart) == 0
    assert cart.total_price == 0.0
    assert cart.total_quantity == 0


def test_cart_add(cart, products):

    cart.add(products[0])
    assert len(cart) == 1
    assert cart.total_price == 15.0
    assert cart.total_quantity == 1

    cart.add(products[1], 2)
    assert len(cart) == 2
    assert cart.total_price == 53.0
    assert cart.total_quantity == 3

    cart.add(products[2], quantity=1)
    assert len(cart) == 3
    assert cart.total_price == 65.0
    assert cart.total_quantity == 4

    assert cart.modified


def populate_cart(cart, products, all=True):
    for index, product in enumerate(products):
        if all or index % 2:
            cart.add(product, 2 if index % 2 else 1)
    if all:
        assert len(cart) == len(products)
        assert cart.total_quantity == 9
        assert cart.total_price == 155.0
    else:
        assert len(cart) == len(products) / 2
        assert cart.total_quantity == 6
        assert cart.total_price == 118.0
    assert cart.modified
    return cart


def test_cart_remove(cart, products):
    cart = populate_cart(cart, products)

    # remove just 1 of item #2
    cart.remove(products[1], 1)
    assert cart.modified
    assert len(cart) == len(products)
    assert cart.total_quantity == 8
    assert cart.total_price == 136.0

    # remove the remainer of item #2
    cart.remove(products[1], 1)
    assert cart.modified
    assert len(cart) == len(products)-1
    assert cart.total_quantity == 7
    assert cart.total_price == 117.0

    # remove all of item #4
    cart.remove(products[3])
    assert cart.modified
    assert len(cart) == len(products)-2
    assert cart.total_quantity == 5
    assert cart.total_price == 107.0


def test_cart_clear(cart, products):
    cart = populate_cart(cart, products)

    cart.clear()
    assert cart.modified
    assert len(cart) == 0
    assert cart.total_quantity == 0
    assert cart.total_price == 0.0


def test_cart_iter(cart, products, monkeypatch):
    cart = populate_cart(cart, products, all=False)

    monkeypatch.setattr(Product, 'objects', ProductManager(products))

    for item in cart:
        assert isinstance(item['product'], Product)
        assert item['quantity'] in (1, 2)
