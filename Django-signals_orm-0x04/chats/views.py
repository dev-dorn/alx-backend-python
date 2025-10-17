from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
# from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter, ConversationFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()



# ViewSet for Conversations
class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at']

    def get_queryset(self):
        """
        This view should return a list of all conversations
        for the currently authenticated user.
        """
        return Conversation.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        participants_ids = request.data.get('participants', [])
        if not participants_ids or not isinstance(participants_ids, list):
            return Response({'error': 'participants must be a list of user IDs'}, status=status.HTTP_400_BAD_REQUEST)
        participants = User.objects.filter(user_id__in=participants_ids)
        if not participants.exists():
            return Response({'error': 'No valid participants found'}, status=status.HTTP_400_BAD_REQUEST)
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



# ViewSet for Messages
class MessageViewSet(viewsets.ModelViewSet):
    # Cache the list view for 60 seconds
    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__email']
    ordering_fields = ['sent_at']

    def get_queryset(self):
        """
        This view should return a list of all messages
        from conversations where the current user is a participant.
        """
        return Message.objects.filter(conversation__participants=self.request.user)

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation')
        message_body = request.data.get('message_body')
        if not conversation_id or not message_body:
            return Response({'error': 'conversation and message_body are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user is a participant in the conversation
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response({'error': 'You are not a participant in this conversation'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Create your views here.
