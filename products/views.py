from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Product, Tag, Color, Material
from .forms import ProductForm 
from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_perms
from django.db import transaction
from django.core.exceptions import PermissionDenied
from cart.models import ShoppingCart
from accounts.models import Store
from reviews.models import Review
from rest_framework import generics, permissions
from rest_framework.permissions import BasePermission
from .serializers import ProductSerializer





# Product Creation View
@login_required
def create_product(request):
    if not request.user.is_seller:
        raise PermissionDenied("Only sellers can create products.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                product = form.save(commit=False)
                product.owner = request.user
                product.publish_status = request.POST.get('status', 'draft')
                product.save()

                colors = form.cleaned_data.get('colors')
                if colors:
                    product.colors.set(colors)

                materials = form.cleaned_data.get('materials')
                if materials:
                    product.materials.set(materials)

                tags = form.cleaned_data.get('tags')
                if tags:
                    product.tags.set(tags)

            messages.success(request, 'Your product has been created successfully!')
            return redirect('all_products')
        else:
            messages.error(request, 'There was an error creating your product. Please fix the issues and try again.')
    else:
        form = ProductForm()

    # Pass colors, tags and materials to the template
    colors = Color.objects.all()
    materials = Material.objects.all()
    tags = Tag.objects.all()

    return render(request, 'create_new_product.html', {'form': form,'colors': colors, 'materials': materials, 'tags': tags})



@login_required
def all_products(request):
    if not request.user.role == 'seller':
        return HttpResponseForbidden("You don't have permission to access this page.")

    created_products = Product.objects.filter(owner=request.user)

    context = {
        'products': created_products,
    }
    return render(request, 'all_products.html', context)




def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, publish_status='published')
    features_list = product.features.split(',')

    reviews = Review.objects.filter(product=product).order_by('-created_at')

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    can_edit = request.user.is_authenticated and request.user.has_perm('change_product', product)
    can_delete = request.user.is_authenticated and (request.user.has_perm('delete_product', product) or request.user.is_staff)

    context = {
        'product': product,
        'features_list': features_list,
        'user': product.owner,
        'can_edit': can_edit, 
        'can_delete': can_delete,  
        'reviews': reviews, 
        'related_products': related_products,  
    }

    return render(request, 'product_detail.html', context)



@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the user has permission to change the product
    if not request.user.has_perm('change_product', product):
        raise PermissionDenied("You do not have permission to edit this product.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)

            product.save()  
            form.save_m2m()
            
            messages.success(request, 'Your product has been updated successfully!')
            return redirect('product_detail', product_id=product.id)
        else:
            messages.error(request, 'There were errors in the form. Please correct them.')
    else:
        form = ProductForm(instance=product)
    
    colors = Color.objects.all() 
    selected_colors = product.colors.all()

    context = {
        'product': product,
        'colors': colors,
        'selected_colors': selected_colors,
        'form': form,
    }

    return render(request, 'edit_product.html', context)



@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the user has permission to delete the product
    if not request.user.has_perm('delete_product', product) and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to delete this product.")

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'The product has been deleted successfully!')
        return redirect('all_products')  





class IsOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.publish_status == 'published' or request.user == obj.owner or request.user.is_staff
        
        #only owners or staff can modify
        return obj.owner == request.user or request.user.is_staff
    




class ProductListCreateAPIView(generics.ListCreateAPIView):
    """
    - GET: List all products
    - POST: Create a new product (Only sellers)
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_seller:
            return Product.objects.all() #only staff and sellers can see all products
        return Product.objects.filter(publish_status='published') #other than them can only see published products

    def perform_create(self, serializer):
        user = self.request.user
        
        # Only sellers can create products
        if not user.is_seller:
            raise PermissionDenied("Only sellers can create products.")

        with transaction.atomic():
            product = serializer.save(owner=user, publish_status=self.request.data.get('status', 'draft'))

            product.colors.set(self.request.data.getlist('colors', []))
            product.materials.set(self.request.data.getlist('materials', []))
            product.tags.set(self.request.data.getlist('tags', []))




class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    - GET: Retrieve product details
    - PUT: Edit product (Only owner or staff)
    - DELETE: Delete product (Only owner or staff)
    """

    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_seller:
            return Product.objects.all()
        return Product.objects.filter(publish_status='published')


    '''def get_object(self):
        obj = get_object_or_404(Product, id=self.kwargs['pk'])
        if obj.publish_status != 'published' and obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to view this product.")
        return obj'''


    def perform_update(self, serializer):
        #only owners can edit their products
        product = self.get_object()
        if not self.request.user.has_perm('change_product', product):
            raise PermissionDenied("You do not have permission to edit this product.")

        serializer.save()


    def perform_destroy(self, instance):
        #only owners or staff can delete a product 
        if not self.request.user.has_perm('delete_product', instance) and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to delete this product.")
        
        instance.delete()



