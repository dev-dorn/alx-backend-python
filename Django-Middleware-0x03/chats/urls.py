from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from . import views
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'message', MessageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  
    path('', views.chat_home, name='chat_home'),
    path('send-message/', views.send_message, name='send_message'),
               
]
