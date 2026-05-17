from django.contrib import admin
from django.contrib import messages
from django_backend.store.models import Category, Product, CartItem, Order, OrderItem


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__username']
    readonly_fields = ['total_price']
    
    def save_model(self, request, obj, form, change):
        """Создание заказа через админку"""
        if not change:
            super().save_model(request, obj, form, change)
            
            cart_items = CartItem.objects.filter(user=obj.user)
            
            if cart_items.exists():

                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=obj,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )

                cart_items.delete()
                messages.success(request, f"Заказ создан из {cart_items.count()} товаров из корзины")
            else:
                messages.warning(request, "Корзина пользователя пуста")
        else:
            super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'get_total']
    list_filter = ['order__status']
    search_fields = ['order__id', 'product__name']
    readonly_fields = ['get_total']
    