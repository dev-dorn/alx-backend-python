from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow authenticated participants of a conversation to access or modify it.
    """

    def has_permission(self, request, view):
        # Only allow authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if hasattr(obj, 'participants'):
            is_participant = request.user in obj.participants.all()
            return is_participant

        # For Message objects
        if hasattr(obj, 'conversation'):
            is_participant = request.user in obj.conversation.participants.all()
            # Only allow unsafe methods (PUT, PATCH, DELETE) for participants
            if request.method in permissions.SAFE_METHODS:
                return is_participant
            elif request.method in ('PUT', 'PATCH', 'DELETE'):
                return is_participant
        return False