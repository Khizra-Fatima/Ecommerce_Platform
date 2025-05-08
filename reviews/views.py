from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from products.models import Product
from orders.models import OrderCheckoutUserInfo
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied



@login_required
def leave_reviews(request, order_id):
    order = get_object_or_404(OrderCheckoutUserInfo, id=order_id, user=request.user)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        
        #Validate rating
        if rating not in ["1", "2", "3", "4", "5"]:
            messages.error(request, "Invalid rating value.")
            return redirect("leave_review", order_id=order.id)

        # Save the review
        Review.objects.create(
            owner=request.user,
            product=order.product,
            order=order,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, "Thank you for your review!")
        return redirect("all_reviews")

    return render(request, "leave_review.html", {"order": order, "product": order.product})



@login_required
def all_reviews(request):
    if request.user.role != 'customer':
        raise PermissionDenied("Only customers can access this page.")


    leaved_reviews = Review.objects.filter(owner=request.user)
    
    context = {
        'leaved_reviews': leaved_reviews,
    }
    return render(request, 'all_reviews.html', context)



@login_required
def seller_reviews(request):
    if request.user.role != 'seller':
        raise PermissionDenied("Only sellers can access this page.")

    seller_reviews = Review.objects.filter(product__owner=request.user)

    return render(request, 'all_reviews.html', {'seller_reviews': seller_reviews})



@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.owner:
        raise PermissionDenied(request, 'You are not allowed to edit this review.')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()  # This saves the review with the updated data from the form
            messages.success(request, 'Your review has been updated successfully!')
            return redirect('all_reviews')
        else:
            messages.error(request, 'There were errors in the form. Please correct them.')
    else:
        form = ReviewForm(instance=review)

    context = {
        'review': review,
        'form': form,
    }

    return render(request, 'edit_review.html', context)



@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.owner:
        messages.error(request, 'You are not allowed to delete this review.')
        return redirect('all_reviews', review_id=review_id)

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'The review has been deleted successfully!')
        return redirect('user_dashboard') 