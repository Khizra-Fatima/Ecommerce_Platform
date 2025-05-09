from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Notification
from orders.models import OrderCheckoutUserInfo
from reviews.models import Review
from products.models import Product



# Seller's Notification
@receiver(post_save, sender=OrderCheckoutUserInfo)
def handle_order_post_save(sender, instance, created, **kwargs):
    print(f"Signal triggered for: {sender.__name__}")
    # Check if the action is created
    if created:
        print(f"Creating notification for order: {instance.order_id}")
    
        try:
            # Notification for a new order
            Notification.objects.create(
                receiver=instance.product.owner,  # Seller
                message=f"New order received: #{instance.order_id}",
                notification_type="order_update",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.order_id
            )
            print("Notification created successfully.")
        except Exception as e:
            print(f"Error creating notification: {e}")



@receiver(post_save, sender=Review)
def handle_review_post_save(sender, instance, created, **kwargs):
    print(f"Signal triggered for: {sender.__name__}")
    # Check if the action is created
    if created:
        print(f"Creating notification for review: {instance.id}")
    
        try:
            # Notification for a new review
            Notification.objects.create(
                receiver=instance.product.owner,  # Get the Seller
                message=f"New review received: #{instance.id}",
                notification_type="review",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )
            print("Notification created successfully.")
        except Exception as e:
            print(f"Error creating notification: {e}")




# Customer's Notification
@receiver(post_save, sender=OrderCheckoutUserInfo)
def notify_customer_order_status(sender, instance, created, **kwargs):
    # Skip notification for newly created orders
    if created:
        return

    # Create a notification when the order status changes
    Notification.objects.create(
        receiver=instance.user, # Get the Customer
        message=f"Your order #{instance.id} status has been updated to '{instance.get_status_display()}'.",
        notification_type="order_update",
    )