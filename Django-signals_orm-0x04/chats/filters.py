import django_filters
from django.db.models import Q
from .models import Message, Conversation
from django.utils import timezone
from datetime import datetime, timedelta

class MessageFilter(django_filters.FilterSet):
    """
    Filter for Message model
    """
    time_range = django_filters.ChoiceFilter(
        choices=[
            ('today', 'Today'),
            ('week', 'Last 7 days'),
            ('month', 'Last 30 days'),
        ],
        method='filter_time_range',
        label='Time Range'
    )
    user = django_filters.CharFilter(method='filter_by_user')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Message
        fields = ['time_range', 'user', 'search']

    def filter_time_range(self, queryset, name, value):
        today = timezone.now().date()
        if value == 'today':
            return queryset.filter(sent_at__date=today)
        elif value == 'week':
            week_ago = today - timedelta(days=7)
            return queryset.filter(sent_at__date__gte=week_ago)
        elif value == 'month':
            month_ago = today - timedelta(days=30)
            return queryset.filter(sent_at__date__gte=month_ago)
        return queryset

    def filter_by_user(self, queryset, name, value):
        return queryset.filter(
            Q(sender__email__icontains=value) |
            Q(sender__username__icontains=value)
        )

    def filter_search(self, queryset, name, value):
        return queryset.filter(message_body__icontains=value)

class ConversationFilter(django_filters.FilterSet):
    """
    Filter for Conversation model
    """
    participant = django_filters.CharFilter(method='filter_by_participant')
    date = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    date_range = django_filters.DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = Conversation
        fields = ['participant', 'date', 'date_range']

    def filter_by_participant(self, queryset, name, value):
        return queryset.filter(
            Q(participants__email__icontains=value) |
            Q(participants__username__icontains=value)
        )