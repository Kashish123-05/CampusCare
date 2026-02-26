from django.contrib import admin
from .models import ChatMessage, FAQ


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['message', 'response']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer', 'keywords']
