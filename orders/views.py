from django.http import JsonResponse
from datetime import timedelta, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from rest_framework.views import APIView
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView
from django.contrib import messages
from .models import OrderCheckoutUserInfo
from .forms import OrderCheckoutForm, OrderStatusUpdateForm
from products.models import Product
from cart.models import ShoppingCart
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user
from django.core.exceptions import PermissionDenied
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from .serializers import OrderCheckoutSerializer



@login_required
def OrderSuccessView(request):
    if request.user.role != 'customer':
        return HttpResponseForbidden("You are not allowed to access this page.")
    return render(request, 'order_success.html')


class OrderCheckoutView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'customer':
            raise PermissionDenied("Only customers can place orders.")
        return super().dispatch(request, *args, **kwargs)
    

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)


        # Fetch the cart item for the current user and product
        cart_item = ShoppingCart.objects.filter(user=request.user, product=product).first()
        cart_color = cart_item.color if cart_item else None
        initial_quantity = cart_item.quantity if cart_item else 1


        # Pre-fill form with user info
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone_number': request.user.profile.phone_number,
            'address': request.user.profile.address,
            'color': cart_color,
        }
        form = OrderCheckoutForm(initial=initial_data, product=product)
        
        context = {
            'form': form,
            'product': product,
            'cart': cart_item,
            'cart_color': cart_color, 
            'initial_quantity': initial_quantity,
            'initial_delivery_method': 'standard',
            'delivery_charges': product.delivery_charges or 0,
            'express_delivery_charge': 20,
            'estimated_delivery_date': date.today() + timedelta(days=5),
        }

        return render(request, 'order_checkout_page.html', context)
    

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = OrderCheckoutForm(request.POST, product=product)

        # Fetch the cart item again for context
        cart_item = ShoppingCart.objects.filter(user=request.user, product=product).first()
        cart_color = cart_item.color if cart_item else None
        initial_quantity = cart_item.quantity if cart_item else 1

        if form.is_valid():
            quantity = int(request.POST.get('quantity', 1))
            delivery_method = request.POST.get('delivery_method')
            delivery_charges = product.delivery_charges or 0

            # Apply express delivery charge if selected
            express_charge = 20 if delivery_method == 'express' else 0
            total_price = product.price * quantity + delivery_charges + express_charge

            delivery_days = 2 if delivery_method == 'express' else 5
            estimated_delivery_date = date.today() + timedelta(days=delivery_days)

            order_info = form.save(commit=False)
            order_info.user = request.user
            order_info.product = product
            order_info.quantity = quantity
            order_info.delivery_method = delivery_method
            order_info.delivery_charges = delivery_charges + express_charge
            order_info.total_price = total_price
            order_info.estimated_delivery_date = estimated_delivery_date
            order_info.color = form.cleaned_data['color']
            order_info.save()

            messages.success(request, 'Your order has been placed successfully!')
            return redirect('order_success')

        # If form is not valid, re-render checkout page with errors
        context = {
            'product': product,
            'form': form,
            'cart': cart_item,
            'cart_color': cart_color,
            'initial_quantity': initial_quantity,
            'initial_delivery_method': 'standard',
            'delivery_charges': product.delivery_charges or 0,
            'express_delivery_charge': 20,
            'estimated_delivery_date': date.today() + timedelta(days=5),
        }

        return render(request, 'order_checkout_page.html', context)



@login_required
def order_list_or_order_history(request):
    orders_list = get_objects_for_user(request.user, 'view_ordercheckoutuserinfo', klass=OrderCheckoutUserInfo)

    if request.user.role != 'customer':
        return HttpResponseForbidden("You are not allowed to access order history.")
    return render(request, 'order_list.html', {'orders_list': orders_list})



@login_required
def seller_orders(request):
    seller_orders = get_objects_for_user(request.user, 'view_ordercheckoutuserinfo', klass=OrderCheckoutUserInfo)

    if request.user.role != 'seller':
        raise PermissionDenied("Only sellers can access this page.")

    return render(request, 'seller_orders.html', {'seller_orders': seller_orders})



@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(OrderCheckoutUserInfo, id=order_id)

     #Check if the current user is the owner of the product
    if order.product.owner != request.user:
        return HttpResponseForbidden("You are not allowed to update the status of this order.")
    
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order status updated successfully.")
            return redirect(reverse('seller_dashboard')) 
        else:
            messages.error(request, 'There were errors in the form. Please correct them.')
    else:
        form = OrderStatusUpdateForm(instance=order)

    return render(request, 'seller_orders.html', {'form': form, 'order': order})



def order_detail(request, order_id):
    order = get_object_or_404(OrderCheckoutUserInfo, id=order_id)
    
    # Check if the current user is either the order's owner or a coadmin
    if order.user != request.user and not request.user.groups.filter(name='Coadmin').exists():
        return HttpResponseForbidden("You are not allowed to view this order.")

    context = {
        'order': order,
    }

    return render(request, 'order_details.html', context)



@login_required
def delete_order_history_product(request, order_product_id):
    order = get_object_or_404(OrderCheckoutUserInfo, id=order_product_id)
    
    if request.user.has_perm('delete_ordercheckoutuserinfo', order) or request.user.role == 'coadmin':
        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('user_dashboard')

    raise PermissionDenied("You do not have permission to delete this order.")



@login_required
def clear_order_history(request):
    if request.method == 'POST':
        OrderCheckoutUserInfo.objects.filter(user=request.user).delete()
        messages.success(request, 'All items have been removed from your order history!')
        return redirect('user_dashboard')
    else:
        return redirect('user_dashboard')   
    



########### API Views ############
class OrderPreFillAPIView(APIView):
    """
    Retrieve pre-filled order details based on the product in the user's cart.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # Fetch the cart item for the current user and product
        cart_item = ShoppingCart.objects.filter(user=request.user, product=product).first()
        cart_color = cart_item.color if cart_item else None
        initial_quantity = cart_item.quantity if cart_item else 1

        # Prepare pre-filled order data
        prefilled_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone_number': request.user.profile.phone_number,
            'address': request.user.profile.address,
            'color': cart_color.id if cart_color else None,  # Send color ID
            'quantity': initial_quantity,
            'delivery_method': 'standard',
            'delivery_charges': product.delivery_charges or 0,
            'express_delivery_charge': 20,
            'estimated_delivery_date': date.today() + timedelta(days=5),
            'product': product.id,
        }

        return Response(prefilled_data)



#order list and create api view
class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderCheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #customers can see only their orders
        return OrderCheckoutUserInfo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        #assign the logged-in user to the order (only customer)
        serializer.save(user=self.request.user)



#order detail, order update, and order delete api view
class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderCheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        #customers can access only their orders.
        #Sellers can access orders related to their products.
        user = self.request.user
        return OrderCheckoutUserInfo.objects.filter(user=user) | OrderCheckoutUserInfo.objects.filter(product__owner=user)



#seller orders api view (list)
class SellerOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderCheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #Sellers can see orders related to their products
        return OrderCheckoutUserInfo.objects.filter(product__owner=self.request.user)
    



#clear order history api view (destroy all)
class ClearOrderHistoryAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #Customers can delete only their orders
        return OrderCheckoutUserInfo.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        #Delete all orders for the logged-in customer
        self.get_queryset().delete()