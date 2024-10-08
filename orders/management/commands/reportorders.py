from django.core.management import BaseCommand

from orders.reporter import report_orders


class Command(BaseCommand):
    def handle(self, *args, **options):
        report_orders()