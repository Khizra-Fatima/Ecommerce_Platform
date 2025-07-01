from django.db import models
from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm

User = get_user_model() 


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    


class Color(models.Model):
    name = models.CharField(max_length=200, unique=True)
    hex_code = models.CharField(max_length=7)

    class Meta:
        verbose_name_plural = "Colors"

    def __str__(self):
        return self.name
    


class Size(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "Sizes"

    def __str__(self):
        return self.name
    


class Material(models.Model):
    name = models.CharField(max_length=225, unique=True)

    class Meta:
        verbose_name_plural = "Materials"

    def __str__(self):
        return self.name
    


class WeightUnit(models.Model):
    name = models.CharField(max_length=225, unique=True)

    class Meta:
        verbose_name_plural = "Weight_units"

    def __str__(self):
        return self.name



class DimensionUnit(models.Model):
    name = models.CharField(max_length=225, unique=True)

    class Meta:
        verbose_name_plural = "Dimension_units"

    def __str__(self):
        return self.name



    





class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    STOCK_STATUS = [
        ('in stock', 'In Stock'),
        ('out of stock', 'Out of Stock'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey('accounts.Store', on_delete=models.CASCADE, related_name='products', null=True)
    product_name = models.CharField(max_length=255, null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=False, blank=False)
    stock = models.IntegerField(default=0, null=False, blank=False)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS, default='in stock')
    colors = models.ManyToManyField(Color, related_name="products")
    features = models.TextField(null=False, blank=False)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_unit = models.ForeignKey(WeightUnit, on_delete=models.SET_NULL, null=True)
    materials = models.ManyToManyField(Material, related_name='products', blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=False)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=False)
    depth = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=False)
    dimension_unit = models.ForeignKey(DimensionUnit, on_delete=models.SET_NULL, null=True, blank=True)
    featured_image = models.ImageField(default='product_images/default_featured_img.jpg', upload_to='product_images/', blank=True, null=True)
    product_video = models.FileField(upload_to='product_videos/', blank=True, null=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    publish_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # assign object-level permissions to the owner
        assign_perm('change_product', self.owner, self)
        assign_perm('delete_product', self.owner, self)

    def __str__(self):
        return f"Product ID: {self.id}, {self.owner} created this product ({self.product_name})"