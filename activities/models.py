from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from products.models import Product

User = get_user_model() 


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} wishlisted {self.product.product_name}"




class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()


    ORDER_UPDATE = 'order_update'
    REVIEW = 'review'
    PROMOTION = 'promotion'
    STOCK_ALERT = 'stock_alert'
    SYSTEM = 'system'


    NOTIFICATION_TYPES = [
        (ORDER_UPDATE, 'Order Update'),
        (REVIEW, 'Review'),
        (PROMOTION, 'Promotion'),
        (STOCK_ALERT, 'Stock Alert'),
        (SYSTEM, 'System'),
    ]
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    read_status = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)



    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=36, null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Notification for {self.receiver} - {self.message[:30]}"

    class Meta:
        ordering = ['-creation_date']





class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    msg_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["sender", "receiver"]),
            models.Index(fields=["read_status"]),
        ]

    def __str__(self):
        return f"Message from {self.sender.first_name} to {self.receiver.first_name} at {self.timestamp}"


