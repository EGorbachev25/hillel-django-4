import random
from time import sleep

from hillelDjango4.celery import app
from telegram.models import TelegramUserAccount
from telegram.service import send_telegram_message
from orders.reporter import report_orders, report_order_stats


@app.task(bind=True)
def send_order_creation_notification(self, order_id):
    print(f"Order {order_id} was created!")
    telegram_id = TelegramUserAccount.objects.get(user_id=1).telegram_id

    send_telegram_message(telegram_id, f"Order {order_id} was created!")

    return f"Order {order_id} was created!"


@app.task(bind=True)
def update_orders_report(self):
    report_orders()


@app.task(bind=True)
def update_orders_total_report(self):
    report_order_stats()


@app.task(bind=True)
def test_celery(self):
    print("Hello from Celery!")
    sleep(5)
    print("Goodbye from Celery!")

    if random.random() < 0.5:
        raise Exception("Random error!")

    return "Success!"
