class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        # Only fetch unread messages for the given user, optimize with .only()
        return self.get_queryset().filter(receiver=user, read=False).only('id', 'sender', 'receiver', 'content', 'timestamp', 'parent_message')
from django.db import models
from .managers import UnreadMessagesManager
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)  # True if message has been edited
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    read = models.BooleanField(default=False)  # True if message has been read

    # Custom manager for unread messages
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:20]}"

    def get_all_replies(self):
        """
        Recursively fetch all replies to this message in a threaded structure.
        Returns a list of dicts: { 'message': Message, 'replies': [...] }
        """
        def fetch_replies(message):
            replies = message.replies.all().select_related('sender', 'receiver').prefetch_related('replies')
            return [
                {
                    'message': reply,
                    'replies': fetch_replies(reply)
                }
                for reply in replies
            ]
        return fetch_replies(self)

# Stores the old content of a message before it was edited
class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edited_histories')

    def __str__(self):
        return f"History for message {self.message.id} at {self.edited_at} (by {self.edited_by})"

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"