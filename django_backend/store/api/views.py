import httpx
import logging
from shared.config import settings
import requests
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from django_backend.store.models import Category, Product, CartItem, Order

from django_backend.store.services.order_service import OrderService
from django_backend.store.services.product_service import ProductService
from django_backend.store.services.cart_service import CartService


from django_backend.store.api.serializers import (
    CategorySerializer,
    ProductSerializer,
    CartItemSerializer,
    OrderSerializer
)

from django_backend.store.domain.exceptions import (
    ProductNotFound,
    ProductValidationError,
    ProductAlreadyExists,
    ProductCategoryNotFound,
    OrderNotFound,
    OrderCancellationError,
    CartItemNotFound,
    CartValidationError, TransactionError, TokenNotFound, BalanceError, EmptyCartError
)



logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    http_method_names = ['get', 'post', 'delete', 'put', 'patch']


class ProductViewSet(viewsets.GenericViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


    def retrieve(self, request, pk = None):
        """GET /api/product/{id}"""
        try:
            product = ProductService.get_product_by_id(pk)
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except ProductNotFound as e:
            return Response(
                {"error": "PRODUCT_NOT_FOUND", "detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )


    def list(self, request):
        """GET /api/product/"""
        category_id = request.query_params.get('category_id')
        search = request.query_params.get('search')
        offset = int(request.query_params.get('offset', 0))
        page_length = int(request.query_params.get('page_length', 20))

        if category_id:
            category_id = int(category_id)

        products = ProductService.get_products(
            category_id=category_id,
            search=search,
            offset=offset,
            page_length=page_length
        )

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


    def create(self, request):
        """POST /api/product/"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            new_product = ProductService.create_product(
                name = data.get('name'),
                price = data.get('price'),
                category_id = data.get('category').id,
                stock = data.get('stock', 0)
            )
            response_serializer = self.get_serializer(new_product)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ProductValidationError as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ProductAlreadyExists as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_409_CONFLICT
            )
        except ProductCategoryNotFound as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )


    def destroy(self, request, pk = None):
        """DELETE /api/product/{id}"""
        try:
            ProductService.delete_product(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductNotFound as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk = None):
        """PUT /api/product/{id}"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            updated_product = ProductService.update_product(
                pk=pk,
                name=data.get('name'),
                price=data.get('price'),
                category_id=data.get('category').id if data.get('category') else None,
                stock=data.get('stock')
            )
            response_serializer = self.get_serializer(updated_product)
            return Response(response_serializer.data)

        except ProductNotFound as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ProductValidationError as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ProductAlreadyExists as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_409_CONFLICT
            )
        except ProductCategoryNotFound as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )




class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, pk=None):
        """DELETE /api/сart/{id}"""
        item = CartItem.objects.filter(pk=pk, user=request.user).first()
        if item is None:
            logger.warning(f"Пользователь попытался удалить несуществующий CartItem")
            return Response(
                data={"detail": f"Cart item with id {pk} not found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )
        product_id = item.product.id
        try:
            CartService.delete_product_from_cart(user=request.user, product_id=product_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ProductNotFound as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except CartItemNotFound as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except CartValidationError as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, pk=None):
        """PUT /api/cart/{id}"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        item = CartItem.objects.filter(pk=pk, user=request.user).first()
        if item is None:
            logger.warning(f"Пользователь попытался удалить несуществующий CartItem")
            return Response(
                data={"detail": f"Cart item with id {pk} not found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )
        product_id = item.product.id
        quantity = data.get('quantity')
        if quantity is None:
            return Response(
                {"detail": "Field 'quantity' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            updated_cart_item = CartService.update_product_quantity(
                user=request.user,
                product_id=product_id,
                quantity=quantity)
            response_serializer = self.get_serializer(updated_cart_item)
            return Response(response_serializer.data)

        except ProductNotFound as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except CartItemNotFound as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except CartValidationError as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        try:
            deleted_cnt = CartService.clear_cart(user=request.user)
            return Response(
                {"deleted_count": deleted_cnt},
                status=status.HTTP_200_OK
            )
        except CartValidationError as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def total(self, request):
        """GET /api/cart/total/"""
        try:
            total = CartService.get_total_price(user=request.user)
            return Response(
                {"total_price": total},
                status=status.HTTP_200_OK
            )
        except CartValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )



def add_to_cart_view(request, product_id):
    try:
        cart_item, product = CartService.add_product_to_cart(
            user=request.user,
            product_id=product_id
        )

        try:
            requests.post(
            f"{settings.TRANSACTION_SERVICE_URL}/internal/notify-cart/",
            json={
                "username": request.user.username,
                "product_name": product.name
            }
            )
            logger.info(f"Уведомление о корзине отправлено")
        except requests.RequestException as e:
            logger.error(f"Ошибка HTTP при уведомлении FastAPI {e}")

        return JsonResponse({"status": "success"})
    except Exception as ex:
        logger.error(f"Ошибка в add_to_cart: {ex}")
        return JsonResponse({"status": "error", "message": str(ex)}, status=500)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        else:
            return Order.objects.filter(user=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            auth_token = None
            if auth_header and auth_header.startswith('Bearer '):
                auth_token = auth_header.split(' ')[1]
            order = OrderService.create_order(request.user, auth_token)
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except EmptyCartError as e:
            return Response({"detail": str(e)}, status=400)
        except BalanceError as e:
            return Response({"detail": str(e)}, status=402)
        except TokenNotFound as e:
            return Response({"detail": str(e)}, status=401)
        except TransactionError as e:
            return Response({"detail": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({"detail": str(e)}, status=500)


def cancel_order_view(request, order_id):
    try:
        order = OrderService.cancel_order(order_id)

        try:
            requests.post(
                f"{settings.TRANSACTION_SERVICE_URL}/internal/notify-cancel-order/",
                json={"username": request.user.username, "order_id": order_id}
            )
            logger.info(f"Запрос на отмену заказа {order_id} передан в FastAPI")
        except requests.RequestException as ex:
            logger.error(f"Не удалось отправить уведомление об отмене заказа {order_id} в FastAPI {ex}")

        return JsonResponse({"status": "success", "message": f"Заказ {order_id} отменен"})

    except OrderNotFound as e:
        logger.warning(f"Попытка отмены несуществующего заказа {order_id}")
        return JsonResponse({"error": "NOT_FOUND", "detail": str(e)}, status=404)
    except OrderCancellationError as e:
        logger.warning(f"Ошибка при отмене заказа {order_id}: {str(e)}")
        return JsonResponse({"error": "CANCELLATION_RESTRICTED", "detail": str(e)}, status=400)