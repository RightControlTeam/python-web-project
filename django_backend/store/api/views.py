from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import viewsets, permissions, filters, status

from store.domain.exceptions import ProductNotFound
from store.models import Category, Product, CartItem, Order
from store.api.serializers import CategorySerializer, ProductSerializer, CartItemSerializer, OrderSerializer
from store.services.order_service import OrderService
from store.services.product_service import ProductService


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


class ProductViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'put', 'patch']
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """/api/product/{id}"""
        try:
            found_product = ProductService.get_product_by_id(kwargs['pk'])
            serializer = self.get_serializer(found_product)
            return Response(serializer.data)
        except ProductNotFound as e:
            return Response(
                {"error": "PRODUCT_NOT_FOUND", "detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def list(self, request, *args, **kwargs):
        """/api/product/"""
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


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
            order = OrderService.create_order(request.user)
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise e