from django.http import JsonResponse, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from .models import Wishlist, Notification, Message
from .forms import MessageForm
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from products.models import Product
from django.db.models import Max, Q
from django.conf import settings
import logging        

logger = logging.getLogger(__name__)









@login_required
def wishlist_product(request, product_id):
    if request.user.role != 'customer':
        raise PermissionDenied("Only customers can Wishlist certain Products.")

    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product_id=product_id)

    if created:
        return JsonResponse({'status': 'wishlisted'})
    else:
        wishlist.delete()
        return JsonResponse({'status': 'removed'})

    


@login_required
def wishlisted_product(request):
    if request.user.role != 'customer':
        raise PermissionDenied("Only customers can access this page.")

    wishlisted = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlisted': wishlisted})




@login_required
def delete_wishlist_item(request, wishlist_id):
    if request.method == 'POST':
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        wishlist_item.delete()
        messages.success(request, 'Item deleted successfully!')
    
    return redirect('wishlisted_product')




@login_required
def clear_wishlist(request):
    if request.method == 'POST':
        Wishlist.objects.filter(user=request.user).delete()
        messages.success(request, 'All items have been removed from your Wishlist!')

    return redirect('wishlisted_product')













@login_required
def notification(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-creation_date')
    print(f"Notifications for {request.user}: {notifications}")
    return render(request, 'notifications.html', {'notifications': notifications})



def delete_list_notification(request, notification_id):
    try:
        notification_item = Notification.objects.get(id=notification_id, receiver=request.user)
        notification_item.delete()
        messages.success(request, 'Notification deleted successfully!')
    except Notification.DoesNotExist:
        messages.error(request, 'Notification not found or access denied.')
    return redirect('notifications')



@login_required
def clear_notification_list(request):
    Notification.objects.filter(receiver=request.user).delete()
    messages.success(request, 'All notifications cleared successfully.')
    return redirect('notifications')



@login_required
@csrf_exempt  # Only needed if not using CSRF in headers
def mark_notification_as_read(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)
        notification.read_status = True
        notification.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


@login_required
def get_notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(receiver=request.user, read_status=False).count()
        return JsonResponse({"count": count})
    return JsonResponse({"count": 0})







@login_required
def msginput(request, user_id):
    user = request.user
    User = get_user_model()
    recipient = get_object_or_404(User, id=user_id)

    if user.role != 'customer':
        return HttpResponseForbidden("Only Customers can message to Sellers.")
    
    if recipient.role != 'seller':
        return HttpResponseForbidden("You can only message sellers.")


    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = user
            message.receiver = recipient
            message.save()
            return redirect('inbox')
    else:
        form = MessageForm()

    context = {
        'form': form,
        'recipient': recipient,
    }

    return render(request, 'msginput.html', context)



@login_required
def msginbox(request):
    user = request.user

    # Fetch latest messages per unique conversation (sender-receiver pair)
    conversations = (
        Message.objects.filter(Q(sender=user) | Q(receiver=user))
        .values('sender', 'receiver')
        .annotate(latest_timestamp=Max('timestamp'))
        .order_by('-latest_timestamp')
    )

    unique_conversations = {}
    
    for conv in conversations:
        user1, user2 = conv['sender'], conv['receiver']
        conversation_key = tuple(sorted([user1, user2]))  # Ensure uniqueness
        if conversation_key not in unique_conversations:
            unique_conversations[conversation_key] = conv

    context = {
        'conversations': [
            {
                'user': get_user_model().objects.get(id=(conv['sender'] if conv['receiver'] == user.id else conv['receiver'])),
                'latest_message': Message.objects.filter(
                    Q(sender=conv['sender'], receiver=conv['receiver']) |
                    Q(sender=conv['receiver'], receiver=conv['sender'])
                ).order_by('-timestamp').first(),
                'latest_timestamp': conv['latest_timestamp']
            }
            for conv in unique_conversations.values()
        ]
    }

    return render(request, 'msginbox.html', context)



@login_required
def msgchatformat(request, user_id):
    user = request.user
    User = get_user_model()
    other_user = get_object_or_404(User, id=user_id)

    if user == other_user:
        return redirect('inbox')

    messages = Message.objects.filter(
        Q(sender=user, receiver=other_user) |
        Q(sender=other_user, receiver=user)
    ).select_related('sender', 'receiver').order_by('timestamp')

    messages.filter(receiver=user, read_status=False).update(read_status=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = user
            message.receiver = other_user
            message.save()

            # If it's an AJAX request, return only the new message
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'partials/message.html', {'message': message, 'user': user})

            return redirect('inbox')

    else:
        form = MessageForm()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'msgchatformat.html', {'messages': messages, 'other_user': other_user, 'form': form})

    return render(request, 'msgchatformat.html', {'messages': messages, 'other_user': other_user, 'form': form})



