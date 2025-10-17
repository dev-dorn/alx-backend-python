
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Message


@require_GET
@login_required
def unread_messages(request):
    """
    Return all unread messages for the logged-in user.
    Optimized with .only() to fetch only required fields.
    """
    unread_qs = (
        Message.unread.unread_for_user(request.user)
        .only("id", "sender_id", "receiver_id", "content", "timestamp")
    )
    data = [
        {
            "id": msg.id,
            "sender": msg.sender_id,
            "receiver": msg.receiver_id,
            "content": msg.content,
            "timestamp": msg.timestamp,
        }
        for msg in unread_qs
    ]
    return JsonResponse({"unread_messages": data})


def build_thread(message):
    """
    Recursively build a threaded structure for a message and its replies.
    """
    return {
        "id": message.id,
        "sender": message.sender_id,
        "receiver": message.receiver_id,
        "content": message.content,
        "timestamp": message.timestamp,
        "replies": [build_thread(reply) for reply in message.replies.all()],
    }


@require_GET
@login_required
@cache_page(60)
def threaded_messages(request):
    """
    Return all top-level messages (no parent) for the user, with threaded replies.
    Optimized with select_related and prefetch_related.
    Optional query params: sender, receiver
    """
    qs = (
        Message.objects.filter(parent_message__isnull=True)
        .select_related("sender", "receiver")
        .prefetch_related("replies")
    )

    sender = request.GET.get("sender")
    receiver = request.GET.get("receiver")

    if sender:
        qs = qs.filter(sender_id=sender)
    if receiver:
        qs = qs.filter(receiver_id=receiver)

    # Default: show messages where user is sender or receiver
    if not sender and not receiver:
        qs = qs.filter(models.Q(sender=request.user) | models.Q(receiver=request.user))

    threads = [build_thread(msg) for msg in qs]
    return JsonResponse({"threads": threads})


@login_required
def delete_user(request):
    """
    Allow the logged-in user to delete their own account.
    """
    if request.method == "POST":
        user = request.user
        user.delete()
        return HttpResponse("Your account and all related data have been deleted.", status=200)

    return HttpResponse("Only POST allowed.", status=405)


User = get_user_model()
