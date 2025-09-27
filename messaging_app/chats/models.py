import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=10,
        choices=[
            ('guest', 'Guest'),
            ('host', 'Host'),
            ('admin', 'Admin'),
        ],
        default='guest'
    )  # Removed the trailing comma here
    created_at = models.DateTimeField(auto_now_add=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. This user will get all the permissions granted to each of their groups.',
        related_name="chat_user_set",
        related_query_name='chat_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user',
        related_name="chat_user_set",
        related_query_name="chat_user",
    )

    class Meta: 
        db_table = 'user'
    
    def __str__(self):
        return self.email

class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation'
        
    def __str__(self):
        participant_names = [user.email for user in self.participants.all()]
        return f"Conversation between {', '.join(participant_names)}"
    
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message'
        ordering = ['sent_at']
        
    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"  # Fixed typo here
