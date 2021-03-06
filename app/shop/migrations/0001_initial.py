# Generated by Django 3.1.3 on 2020-11-07 08:00

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('slug', models.SlugField(max_length=64, unique=True)),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_created', models.DateTimeField(auto_now_add=True)),
                ('dt_updated', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=60, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=60, verbose_name='Last Name')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('address', models.TextField(verbose_name='Address')),
                ('city', models.CharField(max_length=100, verbose_name='City')),
                ('postal_code', models.CharField(max_length=20, verbose_name='Postal Code')),
                ('order_status', models.IntegerField(choices=[(-2, 'Unknown'), (-1, 'Canceled'), (0, 'New'), (1, 'Processing'), (2, 'Dispatched'), (3, 'Completed')], default=0)),
                ('paid_status', models.BooleanField(default=False)),
                ('phone', models.CharField(blank=True, max_length=40, verbose_name='Phone')),
                ('shipping', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_created', models.DateTimeField(auto_now_add=True)),
                ('dt_updated', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(help_text='A unique identifier for this product. Letters, digits, dashes allowed', max_length=16, unique=True, validators=[django.core.validators.RegexValidator(regex=re.compile('^[A-Za-z0-9\\-]+$'))])),
                ('title', models.CharField(help_text='A brief title for this product', max_length=256)),
                ('slug', models.SlugField(editable=False, help_text='Unique string that identifies this product in URLs', max_length=128, unique=True)),
                ('detail', models.TextField(blank=True, default='', help_text='An optional description of this product')),
                ('image', models.ImageField(blank=True, help_text='An optional image of this product', upload_to='products/%Y%m')),
                ('price', models.DecimalField(decimal_places=2, help_text='Unit price for this product', max_digits=10)),
                ('available', models.BooleanField(default=True, help_text='Is this product available?')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='shop.category')),
                ('shipping', models.BooleanField(default=True, help_text='Is there a shipping charge for this product?')),
            ],
            options={
                'ordering': ('code',),
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='shop.product')),
            ],
            options={
                'ordering': ('-order', 'id'),
            },
        ),
        migrations.CreateModel(
            name='ShopSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipping_charge', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('bulk_quantity', models.PositiveIntegerField(default=100, null=True)),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.site')),
                ('bulk_shipping_charge', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('tax_rate', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
