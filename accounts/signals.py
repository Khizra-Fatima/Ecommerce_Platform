from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Store, Profile
from guardian.shortcuts import assign_perm
import logging

logger = logging.getLogger(__name__)

# Signal to create a profile for all new users
@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Ensure a profile is created for each new user
        profile = Profile.objects.create(owner=instance)
        assign_perm('view_profile', instance, profile)
        assign_perm('change_profile', instance, profile)
        logger.info(f"Profile created for {instance.email} with permissions assigned.")



# Signal to create a store only for sellers
@receiver(post_save, sender=CustomUser)
def create_store_for_seller(sender, instance, created, **kwargs):
    if created and instance.role == 'seller':
        profile = Profile.objects.get(owner=instance)
        
        store_name = f"{instance.first_name}'s Store"
        store, store_created = Store.objects.get_or_create(
            owner=instance,
            profile=profile,
            name=store_name
        )
        
        if store_created:
            # Assign object-level permissions
            assign_perm('change_store', instance, store)
            logger.info(f"Store created for seller: {instance.email} and permissions assigned.")
        else:
            logger.info("Store already exists for this seller.")
