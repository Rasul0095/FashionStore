import logging
from src.tasks.celery_app import celery_instance


@celery_instance.task()
def send_order_status_notification_task(data: dict):
    status_messages = {
        "paid": "Ваш заказ оплачен",
        "processing": "Заказ в обработке",
        "shipped": "Заказ отправлен",
        "delivered": "Заказ доставлен",
        "cancelled": "Заказ отменен"
    }

    message = f"""
    Статус вашего заказа #{data["order_number"]} изменен.
    Новый статус: {status_messages.get(data["new_status"], data["new_status"])}
    Сумма заказа: {data["total_amount"]} руб.
    Дата заказа: {data["created_at"]}
    """

    with open("src/notification/notification.txt", mode="a", encoding="utf-8") as file:
        content = f"Статус заказа #{data['order_number']} изменен: {message}"
        file.write(content)

    logging.info(f"Уведомление для заказа #{data['order_number']} отправлено")

