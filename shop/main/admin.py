from django.forms import ModelChoiceField, ModelForm, ValidationError
from django.utils.safestring import mark_safe
from django.contrib import admin
from PIL import Image

from .models import *


class SmartphoneAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and not instance.sd:
            print(instance)
            self.fields['sd_memory_size'].widget.attrs.update({
                'readonly': True, 'style': 'background: lightgray;'
            })
        
    def clean(self):
        cleaned_data = super()
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_memory_size'] = None
        return self.cleaned_data

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_width, min_height = Product.MIN_RESOLUTION
        if img.width < min_width or img.height < min_height:
            raise ValidationError('Loaded image too small...')
        return image

class NotebookAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        min_width, min_height = Product.MIN_RESOLUTION
        self.fields['image'].help_text = mark_safe(
            f'<span style="color: red; font-size: 14px;">Upload image with min resolution {min_width}x{min_height}.<br>Too large image will be resizing.</span>'
        ) 

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_width, min_height = Product.MIN_RESOLUTION
        if img.width < min_width or img.height < min_height:
            raise ValidationError('Loaded image too small...')
        return image

class NotebookAdmin(admin.ModelAdmin):

    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))    
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SmartphoneAdmin(admin.ModelAdmin):

    change_form_template = 'admin.html'
    form = SmartphoneAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)
