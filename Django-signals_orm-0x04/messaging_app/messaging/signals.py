from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification
from django.db.models.signals import pre_save
from .models import MessageHistory
from django.contrib.auth.models import User
from django.db.models.signals import post_delete

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:
        old_msg = Message.objects.get(pk=instance.pk)
        if old_msg.content != instance.content:
            MessageHistory.objects.create(
                message=old_msg,
                old_content=old_msg.content
            )
            instance.edited = True

def delete_related_data(sender, instance, **kwargs):
    from .models import Message, Notification, MessageHistory
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(message__sender=instance).delete()


