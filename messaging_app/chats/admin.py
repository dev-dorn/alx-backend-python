from django.contrib import admin
from .models import User, Conversation, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'get_role_display', 'created_at']
    list_filter = ['created_at']
    def get_role_display(self, obj):
        return obj.get_role_display()
    get_role_display.short_description = 'Role'

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['conversation_id', 'created_at']
    filter_horizontal = ['participants']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'sent_at']