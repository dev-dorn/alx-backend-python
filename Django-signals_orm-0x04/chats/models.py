
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# User model extending AbstractUser
class User(AbstractUser):
	user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
	email = models.EmailField(unique=True, null=False)
	phone_number = models.CharField(max_length=20, null=True, blank=True)
	ROLE_CHOICES = [
		('guest', 'Guest'),
		('host', 'Host'),
		('admin', 'Admin'),
	]
	role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	password = models.CharField(max_length=128, null=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

	def __str__(self):
		return f"{self.email} ({self.role})"


# Conversation model
class Conversation(models.Model):
	conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
	participants = models.ManyToManyField('User', related_name='conversations')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Conversation {self.conversation_id}"


# Message model
class Message(models.Model):
	message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
	sender = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sent_messages')
	conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
	message_body = models.TextField(null=False)
	sent_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Message {self.message_id} from {self.sender.email}"
