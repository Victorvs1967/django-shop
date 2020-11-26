from django.forms import ModelChoiceField, ModelForm, ValidationError
from django.utils.safestring import mark_safe
from django.contrib import admin
from PIL import Image

from .models import *


admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(Product)
