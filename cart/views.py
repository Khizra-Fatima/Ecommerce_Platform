import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import ShoppingCart
from products.models import Product, Color


@login_required
def add_cart_product(request, product_id):
    if request.user.role != 'customer':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        selected_color_id = data.get("color")
        quantity = data.get("quantity")

        try:
            quantity = int(quantity)
            if quantity <= 0:
                return JsonResponse({'status': 'error', 'message': 'Invalid quantity'}, status=400)
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Quantity must be a valid number'}, status=400)

        try:
            selected_color = product.colors.get(id=selected_color_id)
        except Color.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid color selected'}, status=400)

        cart_item, created = ShoppingCart.objects.get_or_create(
            user=request.user, 
            product=product,
            color=selected_color,
            defaults={'quantity': quantity}
        )

    
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

            cart_item.save()

        return JsonResponse({
            'status': 'success', 
            'message': f'{product.product_name} ({selected_color.name}) added to cart', 
            'quantity': cart_item.quantity})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




@login_required
def cart_products(request):
    if request.user.role != 'customer':
        raise PermissionDenied("Only customers can access this page.")
    
    shopping_cart_products = ShoppingCart.objects.filter(user=request.user)


    cart_total = sum((item.product.price * item.quantity) for item in shopping_cart_products) if shopping_cart_products.exists() else 0
    total_quantity = sum((item.quantity) for item in shopping_cart_products) if shopping_cart_products.exists() else 0


    context = {
        'shopping_cart_products': shopping_cart_products,
        'cart_total': cart_total,
        'total_quantity': total_quantity,
    }

    return render(request, 'cart.html', context)




@login_required
def delete_cart_product(request, cart_product_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(ShoppingCart, id=cart_product_id, user=request.user)
        #messages.error(request, 'Invalid request method.')
        #return redirect('user_dashboard')
        cart_item.delete()
        messages.success(request, 'Item deleted successfully!')
        return redirect('cart_products') 

    return redirect('cart_products')




@login_required
def clear_cart(request):
    if request.method == 'POST':
        ShoppingCart.objects.filter(user=request.user).delete()
        messages.success(request, 'All items have been removed from your cart!')
        return redirect('cart_products')
    else:
        return redirect('cart_products')   