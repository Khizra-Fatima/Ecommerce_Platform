from django.db import models
from products.models import Product, Color
from cart.models import ShoppingCart
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm
import uuid

User = get_user_model() 






DELIVERY_CHOICES = [
    ('standard', 'Standard (3-5 business days)'),
    ('express', 'Express (1-2 business days)')
]






class OrderCheckoutUserInfo (models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, null=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    delivery_method = models.CharField(max_length=20, choices=[('standard', 'Standard'), ('express', 'Express')])
    estimated_delivery_date = models.DateField(blank=True, null=True)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)



    def calculate_estimated_delivery_date(self):
        from datetime import date, timedelta
        delivery_days = 2 if self.delivery_method == 'express' else 5
        return date.today() + timedelta(days=delivery_days)


    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity + self.delivery_charges
        self.estimated_delivery_date = self.calculate_estimated_delivery_date()
        super().save(*args, **kwargs)

        # Assign object-level permissions
        assign_perm('view_ordercheckoutuserinfo', self.user, self)
        assign_perm('delete_ordercheckoutuserinfo', self.user, self) 
        assign_perm('view_ordercheckoutuserinfo', self.product.owner, self)

    def __str__(self):
        return f"Order #{self.order_id} by {self.user.first_name} for {self.product.product_name}"
    


