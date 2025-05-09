from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Product, Tag, Category, Color, Size, Material, WeightUnit, DimensionUnit

class ProductAdmin(GuardedModelAdmin):
    #admin configurations
    pass

admin.site.register(Product, ProductAdmin)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Material)
admin.site.register(WeightUnit)
admin.site.register(DimensionUnit)
