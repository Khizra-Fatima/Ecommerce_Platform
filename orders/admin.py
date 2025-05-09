from django.contrib import admin
from .models import OrderCheckoutUserInfo
from guardian.admin import GuardedModelAdmin


class OrderCheckoutUserInfoAdmin(GuardedModelAdmin):
    pass

admin.site.register(OrderCheckoutUserInfo, OrderCheckoutUserInfoAdmin)



