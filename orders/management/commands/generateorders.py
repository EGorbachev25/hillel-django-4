from datetime import date, timedelta, datetime

from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker

from django.core.management.base import BaseCommand

from orders.models import Order, OrderProduct
from products.models import Product


class Command(BaseCommand):
    def __init__(self):
        super().__init__()

        self.fake = Faker()

    def create_order(self):
        yesterday = date.today() - timedelta(days=1)
        random_time = self.fake.time_object()

        created_at = datetime.combine(yesterday, random_time)

        # create fake user
        user = User.objects.create_user(username=self.fake.user_name(), email=self.fake.email())

        # create fake order
        order = Order.objects.create(user=user)
        order.created_at = created_at

        # create fake order products
        products_ids = Product.objects.values_list('id', flat=True)
        quantity = self.fake.random_int(min=1, max=10)

        for _ in range(quantity):
            product_quantity = self.fake.random_int(min=1, max=10)
            product_id = self.fake.random_element(products_ids)

            OrderProduct.objects.create(
                order=order,
                product_id=product_id,
                quantity=product_quantity,
            )

    @transaction.atomic
    def handle(self, *args, **options):
        for _ in range(100):
            self.create_order()
