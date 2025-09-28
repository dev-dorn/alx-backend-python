from rest_framework import permissions
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant of the conversation
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
          
        # For messages, check if user is participant of the message's conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False

class IsMessageSenderOrParticipant(permissions.BasePermission):
    """
    Allow users to edit/delete only their own messages, but read if they are participants
    """
    def has_object_permission(self, request, view, obj):
        # Safe methods (GET, HEAD, OPTIONS) are allowed for participants
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()
            
        # Write methods (PUT, PATCH, DELETE) are only allowed for the message sender
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.sender == request.user
        
        return False

class IsAuthenticatedAndReadOnly(permissions.BasePermission):
    """Allow read-only access to authenticated users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated