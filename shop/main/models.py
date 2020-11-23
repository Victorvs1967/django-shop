import sys
from io import BytesIO
from PIL import Image
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
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

class LatestProductsManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True)
        return products

class LatestProducts:
    objects = LatestProductsManager()

class CategoryManager(models.Manager):

    CATEGORY_COUNT_NAME = {
        'Notebook': 'notebook__count',
        'Smartphone': 'smartphone__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_sidebar(self):
        models = get_models_for_count('notebook', 'smartphone')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data

class Category(models.Model):

    __tablename__ = 'Categories'

    name = models.CharField(max_length=255, verbose_name='Category name')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Product(models.Model):

    class Meta:
        abstract = True

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

    def save(self, *args, **kwargs):
        
        # min_width, min_height = self.MIN_RESOLUTION
        # img = Image.open(self.image)
        # min_width, min_height = self.MIN_RESOLUTION
        # if img.width < min_width or img.height < min_height:
        #     raise MinResolutionErrorExeption('Loaded image too small...')
        # # resize image ---------------
        # new_img = img.convert('RGB')
        # new_img.thumbnail((800, 800), Image.ANTIALIAS)
        # filestream = BytesIO()
        # new_img.save(filestream, 'JPEG', quality=90)
        # filestream.seek(0)
        # self.image = InMemoryUploadedFile(filestream, 'ImageField', self.image.name, 'jpeg/image', sys.getsizeof(filestream), None)

        super().save(*args, **kwargs)

class Notebook(Product):

    size = models.CharField(max_length=255, verbose_name='Size')
    display = models.CharField(max_length=255, verbose_name='Display type')
    processor = models.CharField(max_length=255, verbose_name='Processor type')
    memory = models.CharField(max_length=255, verbose_name='Memory type', null=True)
    video = models.CharField(max_length=255, verbose_name='Video type')
    battery_life = models.CharField(max_length=255, verbose_name='Battery life')

    def __str__(self):
        return f'{self.category.name}: {self.title} ({self.slug})'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

class Smartphone(Product):

    size = models.CharField(max_length=255, verbose_name='Size')
    display = models.CharField(max_length=255, verbose_name='Display type')
    video = models.CharField(max_length=255, verbose_name='Video type')
    memory = models.CharField(max_length=255, verbose_name='Memory type')
    battery = models.CharField(max_length=255, verbose_name='Battery')
    sd = models.BooleanField(default=False, verbose_name='SD card')
    sd_memory_size = models.CharField(max_length=255, null=True, blank=True, verbose_name='SD memory size')
    main_cam_resolution = models.CharField(max_length=255, verbose_name='Main cam rersolution')
    front_cam_resolution = models.CharField(max_length=255, verbose_name='Front cam rersolution')

    def __str__(self):
        return f'{self.category.name}: {self.title} ({self.slug})'

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return f'Cart product: {self.content_object.title}'

    def save(self, *args, **kwargs):
        self.total_price = self.qty * self.content_object.price
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
