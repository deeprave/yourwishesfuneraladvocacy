import re

from django.core.validators import RegexValidator
from django.db import models
from django.forms import forms
from django.urls import reverse
from django.utils.text import slugify


class TimestampMixin:
    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)


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


class Product(models.Model, TimestampMixin):
    RX_PRODUCT_CODE = re.compile(r'^[A-Za-z0-9\-]+$')

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE,)
    code = models.CharField(max_length=16, unique=True, validators=[RegexValidator(regex=RX_PRODUCT_CODE)],
                            help_text='A unique identifier for this product. Lettrs, digits, dashes allowed')
    title = models.CharField(max_length=256, help_text='A brief description of this product')
    slug = models.SlugField(max_length=128, unique=True, editable=False,
                            help_text='Unique string that identifies this product in URLs')
    detail = models.TextField(help_text='An optional detailed description of this product', blank=True, default='')
    image = models.ImageField(upload_to='products/%Y%m', blank=True, help_text='An optional image of this product')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('shop:product-detail', args=[self.slug])

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ('code',)

