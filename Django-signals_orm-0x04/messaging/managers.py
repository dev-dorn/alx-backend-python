from django.db import models

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        # Only fetch unread messages for the given user, optimize with .only()
        return self.get_queryset().filter(receiver=user, read=False).only('id', 'sender', 'receiver', 'content', 'timestamp', 'parent_message')
