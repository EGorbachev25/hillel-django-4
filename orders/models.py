import uuid

from django.core.cache import cache
from django.db import models, transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Order(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    total_price = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField('products.Product', through='OrderProduct')

    @property
    def total_quantity(self):
        return sum([op.quantity for op in self.order_products.all()])

    def update_total_price(self):
        with transaction.atomic():
            self.total_price = sum([op.price for op in self.order_products.all()])
            self.save()


@receiver(post_save, sender=Order)
def order_create_signal(sender, instance, created, **kwargs):
    if created:
        from orders.tasks import send_order_creation_notification, update_orders_report
        send_order_creation_notification.delay(instance.pk)
        update_orders_report.delay()

    cache.delete(f'orders:{instance.user_id}')


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price = models.DecimalField(max_digits=10, decimal_places=2)


@receiver(post_save, sender=OrderProduct)
def update_order_total_price_signal(sender, instance, **kwargs):
    instance.order.update_total_price()


@receiver(post_save, sender=OrderProduct)
def clear_cache(sender, instance, **kwargs):
    cache.delete(f'orders:{instance.order.user_id}')


@receiver(pre_save, sender=OrderProduct)
def update_order_product_price(sender, instance: OrderProduct, **kwargs):
    instance.price = instance.product.price * instance.quantity
