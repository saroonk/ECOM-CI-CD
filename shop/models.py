from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_available(self, quantity=1):
        return self.stock >= quantity


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure only one cart per user or session
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_cart', condition=models.Q(user__isnull=False)),
            models.UniqueConstraint(fields=['session_id'], name='unique_session_cart', condition=models.Q(session_id__isnull=False)),
        ]

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for session {self.session_id}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.cartitem_set.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.razorpay_order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity






class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.PositiveIntegerField()
    message = models.TextField()


