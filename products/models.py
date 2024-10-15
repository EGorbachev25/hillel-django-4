from django.db import models
from django.db.models import Manager, QuerySet, OuterRef, Sum, Subquery
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import OrderProduct


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductQuerySet(QuerySet):
    def popular(self):
        return self.annotate(
            total_quantity=Coalesce(Sum('orderproduct__quantity'), 0, output_field=models.DecimalField())
        ).order_by('-total_quantity')


class ProductManager(Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 99999999.99
    description = models.TextField(blank=True, null=True)
    is_18_plus = models.BooleanField(default=False)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name='products')
    # CASCADE - delete all products in this category
    # SET_NULL - set category to NULL
    # SET_DEFAULT - set category to default value
    # RESTRICT - raise an error
    # DO_NOTHING - do nothing
    # PROTECT - raise an error (same as RESTRICT)

    tags = models.ManyToManyField(Tag, blank=True)

    # Active Record pattern
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    def __str__(self):
        return self.name


@receiver(post_save, sender=Product)
def clear_cache(sender, instance, **kwargs):
    from django.core.cache import cache
    cache.delete('popular_products')

    # Delete all orders cache
    keys = cache.keys('orders:*')
    cache.delete_many(keys)
