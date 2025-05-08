from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderCheckoutUserInfo 
from products.models import Product


@receiver(post_save, sender=OrderCheckoutUserInfo, weak=False)
def update_stock_on_order(sender, instance, created, **kwargs):
    #reduce stock when an order is placed

   if created:
        product = instance.product
        if product.stock >= instance.quantity:
            product.stock -= instance.quantity
        else:
            product.stock = 0  #prevent negative stock
        product.save()