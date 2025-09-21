# chats/serializers.py
from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField(required=True)  # Added CharField
    
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']
    
    def validate_message_body(self, value):
        """Custom validation for message body"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Message body cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Message is too long (max 1000 characters)")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()  # Added SerializerMethodField
    latest_message = serializers.SerializerMethodField()  # Added SerializerMethodField
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'message_count', 'latest_message', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_message_count(self, obj):
        """Return the number of messages in the conversation"""
        return obj.messages.count()
    
    def get_latest_message(self, obj):
        """Return the latest message in the conversation"""
        latest_message = obj.messages.order_by('-sent_at').first()
        if latest_message:
            return MessageSerializer(latest_message).data
        return None

class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participant_ids', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
    
    def validate_participant_ids(self, value):
        """Validate that participant IDs exist and there are at least 2 participants"""
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants")
        
        # Check if all user IDs exist
        from .models import User
        existing_users = User.objects.filter(user_id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("One or more user IDs are invalid")
        
        return value
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.set(participants)
        
        return conversation

class MessageCreateSerializer(serializers.ModelSerializer):
    message_body = serializers.CharField(required=True, max_length=1000)
    
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sender', 'sent_at']
    
    def validate(self, data):
        """Validate that the sender is a participant in the conversation"""
        conversation = data['conversation']
        sender = self.context['request'].user
        
        if not conversation.participants.filter(user_id=sender.user_id).exists():
            raise serializers.ValidationError("Sender must be a participant in the conversation")
        
        return data
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)