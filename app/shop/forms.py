# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Row, Div, Layout, Field, Submit

from .models import Order

__all__ = (
    'CartItemForm',
    'OrderForm',
)


class CartItemForm(forms.Form):
    product_code = forms.CharField(label='Product Code', max_length=16)
    product_quantity = forms.IntegerField(label='Quantity', initial=1)

    def clean_product_code(self):
        return self.cleaned_data['product_code'].upper()[:16]

    def clean_product_quantity(self):
        quantity = int(self.cleaned_data['product_quantity'])
        if quantity < 1:
            quantity = 1
        elif quantity > 100:
            raise ValidationError(_('Invalid quantity'))
        return quantity


class OrderForm(forms.ModelForm):
    # first_name = forms.CharField(label=_('First Name'), max_length=60)
    # last_name = forms.CharField(label=_('Last Name'), max_length=60)
    # email = forms.EmailField(label=_('Email'))
    # phone = forms.CharField(label=_('Phone'), max_length=40, required=False)
    # address = forms.CharField(label=_('Delivery Address'), widget=forms.Textarea(attrs=dict(rows=3)))
    # city = forms.CharField(label=_('City'), max_length=100)
    # postal_code = forms.CharField(label=_('Postal Code'), max_length=20)

    def __init__(self, *args, **kwargs):
        self.cart = kwargs.pop('cart', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field('first_name'),
                Field('last_name'),
                Field('email'),
                Field('phone'),
                css_class='col-md-6'
            ),
            Div(
                Field('address', rows=4),
                Field('city'),
                Field('postal_code'),
                Div(
                    FormActions(
                        Submit('confirm', 'Confirm order', css_class='btn-lg'),
                    ),
                    css_class='text-right pt-2'
                ),
                css_class='col-md-6',
            ),
        )

    def save(self, commit=True):
        if commit:
            self.instance.save(cart=self.cart)
        return self.instance

    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code')
