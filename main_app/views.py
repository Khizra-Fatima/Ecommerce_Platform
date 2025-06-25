from django.shortcuts import render
from django.http import JsonResponse
from products.models import Product, Color
from activities.models import Wishlist
from .forms import ProductFilterForm
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Count
from orders.models import OrderCheckoutUserInfo





def home(request):
    # Get top ordered products
    top_ordered_products = (
        OrderCheckoutUserInfo.objects.values('product')
        .annotate(order_count=Count('order_id'))
        .order_by('-order_count')[:12]
    )

    product_ids = [item['product'] for item in top_ordered_products]
    top_products = Product.objects.filter(id__in=product_ids)
    user_wishlist_ids = set()
    if request.user.is_authenticated:
        user_wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('id', flat=True))

    # Get 3 most recently added products
    latest_products = Product.objects.order_by('-created_at')[:4]

    return render(request, 'home.html', {'top_products': top_products, 'latest_products': latest_products, 'user_wishlist_ids': user_>


def explore_area(request):
    filter_form = ProductFilterForm(request.GET or None)
    # first queryset for published products
    products = Product.objects.filter(publish_status='published')

    if filter_form.is_valid():
        # Filter by other things
        category = filter_form.cleaned_data.get('category')
        size = filter_form.cleaned_data.get('size')
        materials = filter_form.cleaned_data.get('materials')
        colors = filter_form.cleaned_data.get('colors')
        stock_status = filter_form.cleaned_data.get('stock_status')
        sale = filter_form.cleaned_data.get('sale')
        # Price range filter
        price_ranges = filter_form.cleaned_data.get('price_range')
        price_q_objects = Q()
        for range_str in price_ranges:
            min_price, max_price = map(int, range_str.split('-'))
            price_q_objects |= Q(price__gte=min_price, price__lt=max_price)

        # Apply filters
        if category:
            products = products.filter(category__in=category)
        if size:
            products = products.filter(size__in=size)
        if materials:
            products = products.filter(materials__in=materials)
        if colors:
            products = products.filter(colors__in=colors)
        if stock_status:
            products = products.filter(stock_status=stock_status)
        if sale:
            products = products.filter(sale_price__gt=0)
        if price_ranges:
            products = products.filter(price_q_objects)



        query = request.GET.get('query')
        if query:
            products = products.filter(
                Q(product_name__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(category__name__icontains=query) |
                Q(features__icontains=query) |
                Q(size__name__icontains=query) |
                Q(materials__name__icontains=query) |
                Q(price__icontains=query)
            ).distinct()

    # Limit to 12
    products = products[:12]

    return render(request, 'buynow.html', {
        'products': products,
        'filter_form': filter_form,
        'color_queryset': Color.objects.all()
    })



def load_more_products(request):
    offset = int(request.GET.get('offset', 0))
    limit = 8
    products = Product.objects.filter(publish_status='published')[offset:offset + limit]

    #Product data as JSON
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.product_name,
            'price': product.price,
            'sale_price': float(product.sale_price) if product.sale_price is not None else None,
            'stock': product.stock,
            'image_url': product.featured_image.url if product.featured_image else None,
        })

    return JsonResponse({'products': product_data})


def product_list(request):
    user_wishlist = set(Wishlist.objects.filter(owner=request.user).values_list('product_id', flat=True)) if request.user.is_authenti>    products = Product.objects.all()
    return render(request, 'wishlist.html', {'products': products, 'user_wishlist': user_wishlist})
