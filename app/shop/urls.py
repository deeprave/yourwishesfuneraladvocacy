# -*- coding: utf-8 -*-
from  django.urls import path
from . import views


urlpatterns = [
    path('payment/<int:orderid>/', views.PaymentView.as_view(), name='payment'),
    path('order/', views.OrderView.as_view(), name='order'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.cart_additem, name='cart-add'),
    path('cart/remove/', views.cart_removeitem, name='cart-remove'),
    path('cart/clear/', views.cart_clear, name='cart-clear'),
    path('cart/order/', views.create_order, name='create-order'),
    path('category/<slug:slug>/', views.ProductListView.as_view(), name='product-category'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('', views.ProductListView.as_view(), name='products'),
]
