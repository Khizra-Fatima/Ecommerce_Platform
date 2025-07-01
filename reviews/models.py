from django.db import models
from orders.models import OrderCheckoutUserInfo
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model() 



class Rating(models.Model):
    name = models.CharField(max_length= 2 ,unique=True)

    class Meta:
        verbose_name_plural = "Ratings"

    def __str__(self):
        return self.name


class Review(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(OrderCheckoutUserInfo, on_delete=models.CASCADE, related_name='reviews', null=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.owner} - Rating: {self.rating}"