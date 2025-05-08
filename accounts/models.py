from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from guardian.shortcuts import assign_perm
from django.utils.translation import gettext_lazy as _
from PIL import Image





class CustomUserManager(BaseUserManager):
    #Define a manager for the custom user model

    def create_user(self, email, password=None, **extra_fields):
        #Create and return a regular user with an email and password.
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        #Create and return a superuser with admin privileges.
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.ADMIN)

        return self.create_user(email, password, **extra_fields)




class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Role constants
    ADMIN = 'admin'
    COADMIN = 'coadmin'
    SELLER = 'seller'
    CUSTOMER = 'customer'

    # Role choices using the constants
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (COADMIN, 'Coadmin'),
        (SELLER, 'Seller'),
        (CUSTOMER, 'Customer'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) #used for admin site
    date_joined = models.DateTimeField(auto_now_add=True)


    USERNAME_FIELD = 'email'  # Use email as the unique identifier for authentication
    REQUIRED_FIELDS = []  # Email & password are required by default

    objects = CustomUserManager()



    def save(self, *args, **kwargs):
        # Ensure only superusers can assign the 'admin' role
        #if self.role == self.ADMIN and not self.is_superuser:
            #raise ValueError("Only superusers can have the admin role.")
        
        super().save(*args, **kwargs)
        


    def __str__(self):
        return self.email
    

    @property
    def is_seller(self):
        #if the user is seller
        return self.role == self.SELLER




class Profile(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE) 
    image = models.ImageField(default='profile_pictures/default_profile.png', upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True) 
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Social media fields
    instagram = models.URLField(max_length=255, blank=True, null=True)
    facebook = models.URLField(max_length=255, blank=True, null=True)
    twitter = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.owner.first_name}'s Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Assign object-level permissions to the owner
        assign_perm('view_profile', self.owner, self)
        assign_perm('change_profile', self.owner, self)




class Store(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_stores')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=150, blank=True)
    store_number = models.CharField(max_length=15, blank=True, null=True)
    store_location = models.TextField(blank=True, null=True)
    featured_image = models.ImageField(default='store_logo/default_store_logo.jpg', upload_to='store_logo/', blank=True, null=True)
    banner_image = models.ImageField(default='store_banners/default_store_banner.jpg', upload_to='store_banners/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    opening_hours = models.TimeField(null=True, blank=True)
    closing_hours = models.TimeField(null=True, blank=True)
    return_policy = models.TextField(blank=True, help_text="Specify the return policy for the store.")
    shipping_policy = models.TextField(blank=True, help_text="Specify the shipping policy for the store.")


    def save(self, *args, **kwargs):
        # Call the real save() method first
        super().save(*args, **kwargs)

        # Assign object-level permission to the owner
        assign_perm('change_store', self.owner, self)


    def __str__(self):
        return self.name
