import sys
from io import BytesIO
from PIL import Image
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone


User = get_user_model()

def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]

def get_product_url(obj, view_name):
    ct_model = obj.__class__._meta.model_name
    return reverse(view_name, kwargs={'ct_model': ct_model, 'slug': obj.slug})

class MinResolutionErrorExeption(Exception):
    pass

class Category(models.Model):

    __tablename__ = 'Categories'

    name = models.CharField(max_length=255, verbose_name='Category name')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Product(models.Model):

    MIN_RESOLUTION = (400, 400)

    category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Product title')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Image')
    description = models.TextField(verbose_name='Description', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Price')

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    product = models.ForeignKey(Product, verbose_name='Goods', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return f'Cart product: {self.product.title}'

    def save(self, *args, **kwargs):
        self.total_price = self.qty * self.product.price
        super().save(*args, **kwargs)

class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Owner', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name='Final price')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Customer', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Phone')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Address')
    orders = models.ManyToManyField('Order', related_name='related_customer', verbose_name='Customer`s orders')

    def __str__(self):
        return f'Customer: {self.user.first_name} {self.user.last_name}'

class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Order new'),
        (STATUS_IN_PROGRESS, 'Order in progress'),
        (STATUS_READY, 'Order ready'),
        (STATUS_COMPLETED, 'Order comleted')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Self'),
        (BUYING_TYPE_DELIVERY, 'Delivery')
    )

    customer = models.ForeignKey(Customer, verbose_name='Customer', related_name='related_orders', on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, verbose_name='Cart', on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=255, verbose_name='First Name')
    last_name = models.CharField(max_length=255, verbose_name='Last Name')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    address = models.CharField(max_length=1024, null=True, blank=True, verbose_name='Address')
    status = models.CharField(max_length=128, verbose_name='Order status', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=128, verbose_name='Order buying type', choices=BUYING_TYPE_CHOICES, default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Order comment', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Order created date')
    order_date = models.DateField(verbose_name='Get order date', default=timezone.now)

    def __str__(self):
        return str(self.id)
