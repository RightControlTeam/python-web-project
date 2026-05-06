class EmptyCartError(Exception):
    """Ошибка: попытка оформить заказ с пустой корзиной"""
    pass


class ProductNotFound(Exception):
    pass

class ProductAlreadyExists(Exception):
    pass

