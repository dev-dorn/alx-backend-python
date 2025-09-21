# chats/views.py
from rest_framework import viewsets, status, filters  # Added filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend  # Added this import
from .models import Conversation, Message, User
from .serializers import (
    ConversationSerializer, 
    MessageSerializer, 
    ConversationCreateSerializer,
    UserSerializer,
    MessageCreateSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # Added filters
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]  # Added filters
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    filterset_fields = ['participants__user_id']
    ordering_fields = ['created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to an existing conversation"""
        conversation = self.get_object()
        serializer = MessageCreateSerializer(
            data=request.data,
            context={'request': request, 'conversation': conversation}
        )
        
        if serializer.is_valid():
            serializer.save(conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]  # Added filters
    filterset_fields = ['conversation__conversation_id', 'sender__user_id']
    ordering_fields = ['sent_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)