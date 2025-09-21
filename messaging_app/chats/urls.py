# chats/urls.py
from django.urls import path, include
from rest_framework_nested import routers
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Main router
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'conversations', ConversationViewSet)

# Nested router: messages under conversations
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]
