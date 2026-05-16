from ..core.logger import logger

def send_registration_email(username: str):
    logger.info(f" Письмо отправлено Привет, {username}! Добро пожаловать в наш магазин ")

def send_cart_notification(username: str, product_name: str):
    logger.info(f" Пользователь {username} добавил {product_name} в корзину")

def send_order_cancel(username: str, order_id: int):
    logger.info(f" Пользователь {username} отменил заказ {order_id}")

def send_security_alert(username: str):
    logger.info(f" Обнаружен вход в аккаунт {username}")