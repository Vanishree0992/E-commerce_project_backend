from django.db import models
from django.contrib.auth.models import User

# ---------------------------
# Category Model
# ---------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, blank=True, null=True, related_name='subcategories'
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name if not self.parent else f"{self.parent} > {self.name}"


# ---------------------------
# Product Model
# ---------------------------
class Product(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')
    ]
    COLOR_CHOICES = [
        ('Red','Red'), ('Blue','Blue'), ('Green','Green'), ('Yellow','Yellow'),
        ('Black','Black'), ('White','White')
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ---------------------------
# Cart Item
# ---------------------------
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")  # One product per user in cart
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ---------------------------
# Order
# ---------------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(CartItem)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    ordered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ordered_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"
