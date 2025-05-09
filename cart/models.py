from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, Color

User = get_user_model() 


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product', 'color')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} added {self.product.product_name} ({self.color}) to their cart"
