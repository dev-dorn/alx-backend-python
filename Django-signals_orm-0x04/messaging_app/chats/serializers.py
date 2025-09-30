# chats/serializers.py
from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'messages', 'created_at']
        read_only_fields = ['id', 'created_at']

class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    
    class Meta:
        model = Conversation
        fields = ['id', 'participant_ids', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        
        from .models import User
        participants = User.objects.filter(id__in=participant_ids)
        conversation.participants.set(participants)
        
        return conversation