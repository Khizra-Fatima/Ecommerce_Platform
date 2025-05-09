from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Store, Profile
from guardian.admin import GuardedModelAdmin


class StoreAdmin(GuardedModelAdmin):
    #admin configurations
    pass

class ProfileAdmin(GuardedModelAdmin):
    #admin configurations
    pass


admin.site.register(CustomUser)
admin.site.register(Store, StoreAdmin)
admin.site.register(Profile, ProfileAdmin)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']


