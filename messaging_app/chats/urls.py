from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'message', MessageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),             
]
