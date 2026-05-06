class EmptyCartError(Exception):
    """Ошибка: попытка оформить заказ с пустой корзиной"""
    pass



#region product exceptions

class ProductNotFound(Exception):
    pass

class ProductAlreadyExists(Exception):
    pass

class ProductInvalidName(Exception):
    pass

class ProductInvalidPrice(Exception):
    pass

class ProductInvalidCategory(Exception):
    pass

class ProductInvalidStock(Exception):
    pass

class ProductCategoryNotFound(Exception):
    pass
#endregion
