from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ---------------------------
    # API Overview
    # ---------------------------
    path("", views.api_overview, name="api-overview"),

    # ---------------------------
    # Auth endpoints
    # ---------------------------
    path("auth/register/", views.register_user, name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),  # JWT login
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/profile/", views.get_user_profile, name="profile"),

    # ---------------------------
    # Contact endpoint
    # ---------------------------
    path("contact/", views.contact_form, name="contact"),

    # ---------------------------
    # Products & Categories
    # ---------------------------
    path("categories/", views.CategoryListAPIView.as_view(), name="category-list"),
    path("products/", views.ProductListAPIView.as_view(), name="product-list"),
    path("products/<int:pk>/", views.ProductDetailAPIView.as_view(), name="product-detail"),

    # ---------------------------
    # Cart Management
    # ---------------------------
    path("cart/add/", views.add_to_cart, name="add-to-cart"),
    path("cart/view/", views.view_cart, name="view-cart"),
    path("cart/update/<int:cart_item_id>/", views.update_cart_item, name="update-cart-item"),
    path("cart/remove/<int:cart_item_id>/", views.remove_from_cart, name="remove-from-cart"),

    # ---------------------------
    # Orders
    # ---------------------------
    path("order/place/", views.place_order, name="place-order"),
    path("order/track/", views.track_orders, name="track-orders"),
    path("order/update-status/<int:order_id>/", views.update_order_status, name="update-order-status"),
]
