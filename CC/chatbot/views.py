from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .models import ChatMessage, FAQ
from .ai_logic import generate_response, get_gemini_response, get_openai_response
import time
import logging

logger = logging.getLogger(__name__)

# Simple rate limit: max 10 messages per minute per user
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 10


def _check_rate_limit(user_id):
    now = time.time()
    if user_id not in RATE_LIMIT:
        RATE_LIMIT[user_id] = []
    RATE_LIMIT[user_id] = [t for t in RATE_LIMIT[user_id] if now - t < RATE_LIMIT_WINDOW]
    if len(RATE_LIMIT[user_id]) >= RATE_LIMIT_MAX:
        return False
    RATE_LIMIT[user_id].append(now)
    return True


@login_required
@require_POST
def chat_send(request):
    """Handle chatbot message and return response."""
    if not getattr(settings, 'CHATBOT_ENABLED', True):
        return JsonResponse({'error': 'Chatbot is disabled'}, status=403)

    message = request.POST.get('message', '').strip()
    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    if not _check_rate_limit(request.user.id):
        return JsonResponse({'error': 'Rate limit exceeded. Please wait.'}, status=429)

    # Try Gemini first, then OpenAI, then rule-based
    backend_used = "rule_based"
    response_text = get_gemini_response(message, request.user)
    if response_text is not None:
        backend_used = "gemini"
    if response_text is None:
        response_text = get_openai_response(message, request.user)
        if response_text is not None:
            backend_used = "openai"
    if response_text is None:
        response_text = generate_response(request.user, message)

    # Store in DB
    obj = ChatMessage.objects.create(
        user=request.user,
        message=message,
        response=response_text
    )

    return JsonResponse({
        'response': response_text,
        'backend_used': backend_used,
        'timestamp': obj.timestamp.isoformat()
    })


@login_required
@require_GET
def chat_history(request):
    """Get user's chat history."""
    messages = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:20]
    data = [{'message': m.message, 'response': m.response, 'timestamp': m.timestamp.isoformat()} for m in reversed(list(messages))]
    return JsonResponse({'messages': data})


def chatbot_enabled(request):
    """Check if chatbot is enabled."""
    return JsonResponse({'enabled': getattr(settings, 'CHATBOT_ENABLED', True)})
