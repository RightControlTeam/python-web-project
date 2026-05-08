class EmptyCartError(Exception):
    """Ошибка: попытка оформить заказ с пустой корзиной"""
    pass



#region product exceptions
class ProductNotFound(Exception):
    pass

class ProductAlreadyExists(Exception):
    pass

class ProductValidationError(Exception):
    pass

class ProductCategoryNotFound(Exception):
    pass
#endregion
