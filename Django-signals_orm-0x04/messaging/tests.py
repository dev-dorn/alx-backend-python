from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class MessagingSignalTest(TestCase):
    def test_notification_created_on_message(self):
        sender = User.objects.create_user(username='sender', password='pass')
        receiver = User.objects.create_user(username='receiver', password='pass')
        msg = Message.objects.create(sender=sender, receiver=receiver, content='Hello!')
        self.assertTrue(Notification.objects.filter(user=receiver, message=msg).exists())
