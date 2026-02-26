from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('send/', views.chat_send, name='chat_send'),
    path('history/', views.chat_history, name='chat_history'),
    path('enabled/', views.chatbot_enabled, name='chatbot_enabled'),
]
