#region product exceptions

class EmptyCartError(Exception):
    pass

class OrderNotFound(Exception):
    pass

class OrderCancellationError(Exception):
    pass

class ProductNotFound(Exception):
    pass

class ProductAlreadyExists(Exception):
    pass

class ProductValidationError(Exception):
    pass

class ProductCategoryNotFound(Exception):
    pass

class CartItemNotFound(Exception):
    pass

class CartValidationError(Exception):
    pass
#endregion
