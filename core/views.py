from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import status, generics, filters
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    CartItemSerializer, OrderSerializer, RegisterSerializer,
    CategorySerializer, UserSerializer, ContactSerializer, ProductSerializer
)
from .models import Product, Category, CartItem, Order

# ---------------------------
# Pagination Class
# ---------------------------
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

# ---------------------------
# API Overview
# ---------------------------
@api_view(["GET"])
def api_overview(request):
    return Response({"message": "E-commerce API is running ✅"})

# ---------------------------
# Register User
# ---------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully ✅"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------
# User Profile
# ---------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# ---------------------------
# Contact Form
# ---------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def contact_form(request):
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data["name"]
        email = serializer.validated_data["email"]
        subject = serializer.validated_data["subject"]
        message = serializer.validated_data["message"]

        full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"
        try:
            send_mail(
                subject,
                full_message,
                email,                          # from user
                [settings.EMAIL_HOST_USER],     # to admin
                fail_silently=False,
            )
            return Response({"message": "Email sent successfully ✅"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------
# Cart Management
# ---------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    try:
        cart_item, created = CartItem.objects.get_or_create(user=user, product_id=product_id)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    serializer = CartItemSerializer(cart_items, many=True)
    total = sum([item.product.price * item.quantity for item in cart_items])
    return Response({"cart": serializer.data, "total_amount": total})

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_cart_item(request, cart_item_id):
    quantity = int(request.data.get("quantity", 1))
    if quantity < 1:
        return Response({"error": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
        cart_item.delete()
        return Response({"message": "Item removed from cart ✅"}, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

# ---------------------------
# Orders Management
# ---------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_order(request):
    user = request.user
    shipping_address = request.data.get("shipping_address")
    cart_items = CartItem.objects.filter(user=user)
    if not cart_items.exists():
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    total_amount = sum([item.product.price * item.quantity for item in cart_items])
    order = Order.objects.create(user=user, total_amount=total_amount, shipping_address=shipping_address)
    order.products.set(cart_items)
    order.save()
    cart_items.delete()
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def track_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_order_status(request, order_id):
    status_value = request.data.get("status")
    if status_value not in ["Pending", "Processing", "Shipped", "Delivered"]:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        order = Order.objects.get(id=order_id)
        order.status = status_value
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

# ---------------------------
# Category List
# ---------------------------
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# ---------------------------
# Product List with Pagination, Filtering, Sorting
# ---------------------------
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'category': ['exact'],
        'size': ['exact'],
        'color': ['exact'],
        'price': ['gte', 'lte'],
        'rating': ['gte', 'lte'],
    }
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'rating', 'created_at', 'discount_price']
    ordering = ['created_at']  # newest first

# ---------------------------
# Product Detail
# ---------------------------
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]  # admin only
