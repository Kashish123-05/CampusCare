"""Load default FAQ entries."""
from django.core.management.base import BaseCommand
from chatbot.models import FAQ


class Command(BaseCommand):
    help = 'Load default FAQ entries'

    def handle(self, *args, **options):
        faqs = [
            {'question': 'How do I report an issue?', 'answer': 'Go to Issues > Submit Issue and fill in the form with title, description, category, and location.', 'keywords': 'report,submit,how'},
            {'question': 'How long does it take to resolve?', 'answer': 'Resolution time depends on priority. Critical issues are addressed first. You can track status in the Issues section.', 'keywords': 'how long,when,resolve,time'},
            {'question': 'What if my WiFi is not working?', 'answer': 'Select Network category when reporting. Try restarting your device first.', 'keywords': 'wifi,internet,network'},
            {'question': 'Who do I contact for urgent issues?', 'answer': 'Submit the issue with Critical priority. For emergencies, contact campus security.', 'keywords': 'urgent,contact,emergency'},
        ]
        for faq in faqs:
            FAQ.objects.get_or_create(question=faq['question'], defaults={'answer': faq['answer'], 'keywords': faq['keywords']})
        self.stdout.write('Loaded %d FAQs' % len(faqs))
