import uuid
from django.db import models, transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from products.models import Product


class Order(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    total_price = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField(Product, through='OrderProduct')

    @property
    def total_quantity(self):
        return sum([op.quantity for op in self.order_products.all()])


@receiver(post_save, sender=Order)
def order_create_signal(sender, instance, created, **kwargs):
    if created:
        from orders.tasks import send_order_creation_notification, update_orders_report
        send_order_creation_notification.delay(instance.pk)
        update_orders_report.delay()


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price = models.DecimalField(max_digits=10, decimal_places=2)


@receiver(post_save, sender=OrderProduct)
def update_order_total_price(sender, instance, **kwargs):
    with transaction.atomic():
        order = instance.order
        order.total_price = sum([op.price for op in order.order_products.all()])
        order.save()


@receiver(pre_save, sender=OrderProduct)
def update_order_product_price(sender, instance: OrderProduct, **kwargs):
    instance.price = instance.product.price * instance.quantity
