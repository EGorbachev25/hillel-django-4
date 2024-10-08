from google_sheets.service import write_to_sheet
from orders.models import Order


def report_orders():
    orders = Order.objects.all().prefetch_related('products').order_by('created_at')

    sheets_data = []

    for order in orders:
        django_admin_link = "http://localhost:8000/admin/orders/order/{}/change/".format(order.uuid)

        sheets_data.append([
            str(order.uuid),
            order.user.email,
            float(order.total_price),
            float(order.total_quantity),
            django_admin_link,
            order.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    write_to_sheet("A2:F", sheets_data)


def report_order_stats():
    orders = Order.objects.all().prefetch_related('products').order_by('created_at')

    total_orders = orders.count()
    total_products = sum([order.total_quantity for order in orders])
    total_price = sum([order.total_price for order in orders])

    sheets_data = [
        ["Total Orders", total_orders],
        ["Total Products", float(total_products)],
        ["Total Price", float(total_price)]
    ]

    write_to_sheet("Total!A1:B", sheets_data)
