# -*- coding: utf-8 -*-
from  django.urls import path
from . import views


urlpatterns = [
    path('', views.ProductListView.as_view(), name='products'),
    path('category/<slug:slug>/', views.ProductListView.as_view(), name='product-category'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('cart-add/<slug:slug>/', views.add_to_cart, name ='cart-add')
]
