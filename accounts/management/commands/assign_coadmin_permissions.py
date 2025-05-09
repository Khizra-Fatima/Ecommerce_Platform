from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from accounts.models import CustomUser

class Command(BaseCommand):
    help = "Assign permissions to the co-admin user"

    def handle(self, *args, **kwargs):
        try:
            coadmin = CustomUser.objects.get(role='coadmin')
            permission = Permission.objects.get(codename='can_view_admin_dashboard')
            coadmin.user_permissions.add(permission)
            coadmin.save()

            self.stdout.write(self.style.SUCCESS(f"Permissions assigned to {coadmin.email}"))
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR("No co-admin user found"))