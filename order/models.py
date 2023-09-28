from django.db import models
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property

from product.models import Product


User = get_user_model()


class Order(models.Model):
    PENDING = 'P'
    SHIPPED = 'S'
    DELIVERED = 'D'
    CANCELLED = 'C'

    STATUS_CHOICES = (
        (PENDING, 'pending'), (SHIPPED, 'shipped'),
        (DELIVERED, 'delivered'), (CANCELLED, 'cancelled')
    )

    buyer = models.ForeignKey(
        User, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return f"{self.buyer}"

    @cached_property
    def total_cost(self):
        """
        Total cost of all the items in an order
        """
        return round(sum([order_item.cost for order_item in self.order_items.all()]), 2)


class DeliveryAddress(models.Model):
    order = models.OneToOneField(
        Order, related_name="order_address", on_delete=models.CASCADE
    )
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.order}, {self.city}, {self.street_address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="product_orders", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return f'{self.order}, {self.product}, {self.quantity}'

    @cached_property
    def cost(self):
        """
        Total cost of the ordered item
        """
        return round(self.quantity * self.product.price, 2)
