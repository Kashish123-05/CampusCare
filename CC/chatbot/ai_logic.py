"""AI/rule-based logic for CampusCare chatbot."""
import re
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from issues.models import Issue

User = get_user_model()
logger = logging.getLogger(__name__)

# Intent keywords for rule-based matching
INTENTS = {
    'report_issue': ['report', 'submit', 'file', 'lodge', 'complaint', 'issue', 'problem', 'broken', 'not working'],
    'track_issue': ['status', 'track', 'update', 'my complaint', 'my issue', 'last complaint', 'progress'],
    'faq': ['how', 'what', 'when', 'where', 'who', 'why', 'faq', 'help', 'guide'],
    'contact_admin': ['contact', 'admin', 'speak', 'talk', 'human', 'representative'],
    'troubleshooting': ['fix', 'troubleshoot', 'solve', 'myself', 'before reporting', 'steps'],
}

# Category suggestion keywords
CATEGORY_KEYWORDS = {
    'electrical': ['light', 'bulb', 'power', 'electricity', 'outlet', 'switch', 'fuse', 'wiring'],
    'plumbing': ['leak', 'pipe', 'water', 'toilet', 'faucet', 'drain', 'flood', 'plumbing'],
    'network': ['wifi', 'internet', 'network', 'connection', 'router', 'slow', 'down'],
    'cleanliness': ['dirty', 'clean', 'trash', 'garbage', 'spill', 'mess', 'sanitation'],
    'classroom_equipment': ['projector', 'whiteboard', 'computer', 'desk', 'chair', 'ac', 'equipment'],
}


def suggest_category(text):
    """Suggest issue category based on user text."""
    text_lower = text.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    return 'other'


def detect_intent(text):
    """Detect user intent from message."""
    text_lower = text.lower().strip()
    for intent, keywords in INTENTS.items():
        if any(kw in text_lower for kw in keywords):
            return intent
    return 'faq'  # default


def get_faq_response(text, user=None):
    """Match against FAQ model or fallback to hardcoded FAQs."""
    from .models import FAQ
    text_lower = text.lower()
    faqs = FAQ.objects.filter(is_active=True)
    for faq in faqs:
        kws = [k.strip().lower() for k in faq.keywords.split(',') if k.strip()]
        if any(kw in text_lower for kw in kws):
            return faq.answer
    # Hardcoded fallbacks
    hardcoded = [
        {'q': ['how to report', 'submit issue', 'report a problem'],
         'a': 'To report an issue, go to Issues > Submit Issue and fill in the form with title, description, category, and location.'},
        {'q': ['where to report', 'report location'],
         'a': 'You can report issues from the Submit Issue page accessible from your dashboard or the navigation menu.'},
        {'q': ['how long', 'resolution time', 'when will it be fixed'],
         'a': 'Resolution time depends on priority. Critical issues are addressed first. You can track your issue status in the Issues section.'},
        {'q': ['electrical', 'lights', 'power'],
         'a': "For electrical issues like lights or power, select 'Electrical' as the category when reporting. Include building and room number."},
        {'q': ['plumbing', 'leak', 'water'],
         'a': "For plumbing issues, select 'Plumbing' as the category. If it's urgent (flooding), mark priority as High or Critical."},
        {'q': ['wifi', 'internet', 'network'],
         'a': "For WiFi or network issues, select 'Network' category. Try restarting your device before reporting."},
    ]
    for item in hardcoded:
        if any(k in text_lower for k in item['q']):
            return item['a']
    return "I'm not sure about that. You can submit an issue from the Issues menu, or contact admin for help."


def get_user_last_issue(user):
    """Get user's latest reported issue."""
    if not user or not user.is_authenticated:
        return None
    return Issue.objects.filter(reported_by=user).order_by('-created_at').first()


def generate_response(user, message):
    """Generate chatbot response based on message and user context."""
    message = message.strip()
    if not message:
        return "Please type a message."

    intent = detect_intent(message)

    if intent == 'report_issue':
        suggested = suggest_category(message)
        cat_display = dict(Issue.CATEGORY_CHOICES).get(suggested, suggested)
        return f"To report this issue, go to **Submit Issue** from the menu. Based on your description, I suggest category: **{cat_display}**. Fill in the form and upload a photo if possible."

    if intent == 'track_issue':
        issue = get_user_last_issue(user)
        if issue:
            return f"Your latest issue: **{issue.title}** — Status: **{issue.get_status_display()}**. View full details in the Issues section."
        return "You haven't reported any issues yet. Go to Submit Issue to report one."

    if intent == 'contact_admin':
        return "To contact admin, please use the Contact or Help section, or email your campus admin. You can also check your issue status in the Issues dashboard."

    if intent == 'troubleshooting':
        return "Before reporting: 1) Check if it's a simple fix (e.g., restart device for WiFi). 2) Note the exact location. 3) Take a photo if safe. If the problem persists, submit an issue with these details."

    # FAQ or default
    return get_faq_response(message, user)


def get_gemini_response(message, user):
    """Use Google Gemini API for AI responses."""
    if not getattr(settings, 'CHATBOT_USE_GEMINI', False):
        return None
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "You are CampusCare assistant for campus maintenance issues. Be concise. "
            "Help users report issues, track status, answer FAQs. Suggest checking Issues section for status. "
            "Guide to Submit Issue for new reports.\n\nUser: "
        ) + message
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else None
    except Exception:
        logger.exception("Gemini response generation failed")
        return None


def get_openai_response(message, user):
    """Optional: Use OpenAI API if configured."""
    if not getattr(settings, 'CHATBOT_USE_OPENAI', False):
        return None
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        system = "You are CampusCare assistant. Help users report campus maintenance issues, track status, and answer FAQs. Be concise."
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message}
            ],
            max_tokens=200
        )
        return resp.choices[0].message.content
    except Exception:
        return None
