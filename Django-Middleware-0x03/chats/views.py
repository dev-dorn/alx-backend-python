from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    ConversationCreateSerializer,
    MessageCreateSerializer
)
from .permissions import IsParticipantOfConversation, IsMessageSenderOrParticipant
from .pagination import MessagePagination
from .filters import MessageFilter, ConversationFilter

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ConversationFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        # Only show conversations where the user is a participant
        return Conversation.objects.filter(participants=self.request.user)
    
    def perform_create(self, serializer):
        conversation = serializer.save()
        # Automatically add the current user as a participant
        conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        
        # Check if user is participant of the conversation
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant of this conversation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(conversation=conversation, sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        participant_email = request.data.get('email')
        
        if not participant_email:
            return Response(
                {'error': 'Email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(email=participant_email)
            conversation.participants.add(user)
            return Response({'status': 'Participant added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageSenderOrParticipant]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MessageFilter
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        # Only show messages from conversations where user is participant
        queryset = Message.objects.filter(conversation__participants=self.request.user)
        conversation_id = self.request.query_params.get('conversation_id')
        
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)