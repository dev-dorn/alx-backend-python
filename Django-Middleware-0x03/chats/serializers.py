from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']

class MessageSerializer (serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
        
class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True
    )
    
    class Meta:
        model = Conversation
        fields = ['participant_emails']
    
    def create(self, validated_data):
        participant_emails = validated_data.pop('participant_email')
        conversation = Conversation.objects.create()
        
        #Add participant email
        for email in participant_emails:
            try:
                user = User.objects.get(email=email)
                conversation.participants.ass(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with email {email} does not exist")
            
            return conversation
        
class MessageCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'message_body']
          