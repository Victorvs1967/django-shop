# Generated by Django 3.1.1 on 2020-09-18 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_smartphone_sd_memory_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smartphone',
            name='sd_memory_size',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='SD memory size'),
        ),
    ]