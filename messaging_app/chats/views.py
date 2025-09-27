from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    ConversationCreateSerializer,
    MessageCreateSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset=Conversation.objects.all()
    
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        serializer = MessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        queryset = Message.objects.all()
        conversation_id = self.request.query_params.get('conversation_id')
        
        if conversation_id:
            queryset = queryset.filter(conversation_conversation_id=conversation_id)
            
        return queryset
     