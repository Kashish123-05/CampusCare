from django.conf import settings


def chatbot_context(request):
    """Add chatbot visibility to all templates."""
    return {
        'chatbot_enabled': getattr(settings, 'CHATBOT_ENABLED', True),
    }
