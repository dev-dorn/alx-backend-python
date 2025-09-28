import django_filters
from .models import Message, Conversation

class MessageFilter(django_filters.FilterSet):
    conversation = django_filters.UUIDFilter(field_name='conversation__conversation_id')
    sender = django_filters.CharFilter(field_name='sender__email')
    start_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    search = django_filters.CharFilter(field_name='message_body', lookup_expr='icontains')
    
    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'start_date', 'end_date', 'search']

class ConversationFilter(django_filters.FilterSet):
    participant = django_filters.CharFilter(field_name='participants__email')
    start_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Conversation
        fields = ['participant', 'start_date', 'end_date']