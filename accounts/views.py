from django.http import HttpResponseForbidden, Http404, JsonResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q, Sum, F, DateField
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from datetime import datetime
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.contrib.auth import logout, get_backends, authenticate, login as auth_login, update_session_auth_hash
from .forms import CustomUserCreationForm, LoginForm, ProfileForm, UserUpdateForm, PasswordChangeForm, StoreForm
from django.contrib import messages
from django.contrib.auth.models import Permission
from orders.models import OrderCheckoutUserInfo
from products.models import Product, Category
from .models import Store, Profile, CustomUser
from django.core.exceptions import PermissionDenied
from guardian.shortcuts import get_perms, get_objects_for_user
from guardian.decorators import permission_required_or_403






####################Co-Admin Related Views#######################
@login_required
def admin_dashboard(request):
    if request.user.role != 'coadmin':
        return HttpResponseForbidden("You don't have permission to access this page.")

    return render(request, 'admin_templates/admin_dashboard.html', {
    })


def overview(request):
    orders = OrderCheckoutUserInfo.objects.all()
    products = Product.objects.all()
    sellers = CustomUser.objects.filter(role = 'seller').count()
    customers = CustomUser.objects.filter(role = 'customer').count()
    users = sellers + customers
    total_revenue = (
        OrderCheckoutUserInfo.objects.filter(status='delivered')
        .aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0
    )


    context = {
        'welcome_message': 'Welcome to your admin dashboard!',
        'orders': orders,
        'total_revenue': total_revenue,
        'products': products,
        'users': users,
        'sellers': sellers,
        'customers': customers,

    }
    return render(request, 'admin_templates/overview.html', context)



def manage_users(request):
    users = CustomUser.objects.filter(Q(role='seller') | Q(role='customer'))
    products = Product.objects.all()

    context = {
        'users': users,
        'products': products, 
    }
    return render(request, 'admin_templates/user_management.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.role == 'coadmin')
def delete_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.role in ['seller', 'customer']:
            user.delete()
            messages.success(request, f"User {user.email} has been deleted successfully.")
        else:
            messages.error(request, "You are not allowed to delete this user.")
    except CustomUser.DoesNotExist:
        messages.error(request, "User does not exist.")
    
    return redirect('admin_dashboard')


def manage_products(request):
    users = CustomUser.objects.filter(Q(role='seller') | Q(role='customer'))
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        'users': users,
        'products': products, 
        'categories': categories,
    }
    return render(request, 'admin_templates/product_management.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.role == 'coadmin')
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, f"Product {product.product_name} has been deleted successfully.")
    except Product.DoesNotExist:
        messages.error(request, "Product does not exist.")
    
    return redirect('admin_dashboard')


def manage_orders(request):
    orders = OrderCheckoutUserInfo.objects.all()
    products = Product.objects.all()

    context = {
        'orders': orders,
        'products': products, 
    }
    return render(request, 'admin_templates/order_management.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.role == 'coadmin')
def delete_order(request, order_id):
    try:
        order = OrderCheckoutUserInfo.objects.get(id=order_id)
        order.delete()
        messages.success(request, f"Order {order.product.product_name} has been deleted successfully.")
    except OrderCheckoutUserInfo.DoesNotExist:
        messages.error(request, "Order does not exist or cannot be deleted.")
    
    return redirect('admin_dashboard')














####################Other Account's App Views#######################
@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    return render(request, 'seller_templates/seller_dashboard.html')



def seller_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    has_permission = request.user.has_perm('change_store', store)
    products = store.products.filter(publish_status="published").order_by('-created_at')

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'store': store,
        'has_permission': has_permission,
        'products': page_obj,
    }

    return render(request, 'seller_templates/seller_store.html', context)



@login_required
@permission_required_or_403('change_store', (Store, 'id', 'store_id'))
def edit_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your Store has been updated successfully!')
            return redirect('seller_store', store_id=store.id)
        else:
            messages.error(request, 'There were errors in the form. Please correct them.')
    else:
        form = StoreForm(instance=store)
    
    context = {
        'form': form,
        'store': store,
    }

    return render(request, 'seller_templates/edit_store.html', context)



@login_required
def user_dashboard(request):
    if request.user.role != 'customer':
        return HttpResponseForbidden("You don't have permission to access this page.")
    return render(request, 'user_templates/user_dashboard.html')



@login_required
def support(request):
    return render(request, "support.html")




@login_required
def user_profile(request, owner_id):
    profile = get_object_or_404(Profile, owner_id=owner_id)

    # Check if the user has the 'view_profile' permission or is a staff member
    has_permission = request.user.has_perm('view_profile', profile) or request.user.is_staff

    if not has_permission:
        raise PermissionDenied("You do not have permission to view this profile.")

    return render(request, 'profile/user_profile.html', {'profile': profile, 'has_permission': has_permission})




@login_required
def edit_profile(request, owner_id):
    try:
        profile = Profile.objects.get(owner_id=owner_id)
    except Profile.DoesNotExist:
        raise Http404("Profile does not exist.")

    # Ensure the user has permission to edit the profile
    if not request.user.has_perm('change_profile', profile):
        raise PermissionDenied("You do not have permission to edit this profile.")

    # Initialize forms
    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    password_form = PasswordChangeForm(request.user, request.POST)

    # Handle form submission
    if request.method == 'POST':
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()

            # Handle password change
            if 'password_submit' in request.POST and password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
            else:
                messages.error(request, 'Please correct the password errors.')

            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile', owner_id=request.user.id)

    # Pass forms to the template
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'password_form': password_form,
    }

    return render(request, 'profile/edit_profile.html', context)






















####################Register, Login, and Account Setting Views#######################
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Find the correct backend and log the user in
            backend = get_backends()[0]  # Using the first backend (custom one)
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            
            auth_login(request, user)  # Log in the user after registration
            return redirect('home')  # Redirect to home or any page
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})


def social_login(request, provider):
    # Use the provider name (like 'google' or 'facebook') to authenticate the user
    return redirect(f'/social-auth/{provider}/')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def data_deletion(request):
    return render(request, 'data_deletion.html')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST, request=request)  # Pass the request to the form
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, email=email, password=password)
            if user is not None:
                auth_login(request, user)  # Log in the user
                next_url = request.GET.get('next', 'home')  # Redirect to 'next' URL or home
                return redirect(next_url)
            else:
                form.add_error(None, "Invalid email or password")
        else:
            print(form.errors)  # Check the errors
    else:
        form = LoginForm(request=request)  # Pass the request to the form

    return render(request, 'login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to home page after logout


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        return redirect("account_deleted")  # Redirect to a "goodbye" page
    return render(request, "accounts/confirm_delete.html")


@login_required
def account_settings(request):
    return render(request, 'acc_settings.html')












