
from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    # Example usage of CharField
    display_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at', 'display_name'
        ]

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'message_body', 'sent_at', 'conversation'
        ]
        read_only_fields = ['message_id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'created_at', 'messages'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'messages']

    def get_messages(self, obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data

# Example of ValidationError usage
def validate_role(value):
    allowed_roles = ['guest', 'host', 'admin']
    if value not in allowed_roles:
        raise serializers.ValidationError(f"Role must be one of {allowed_roles}")
    return value
