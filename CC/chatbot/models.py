from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    """Chat history for the AI chatbot."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class FAQ(models.Model):
    """FAQ entries for chatbot responses."""
    question = models.CharField(max_length=500)
    answer = models.TextField()
    keywords = models.CharField(max_length=500, help_text='Comma-separated keywords for matching')
    category = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question']
