"""
Django settings for CampusCare project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables (optional: pip install django-environ and create .env)
def _env(key, default=''):
    return os.environ.get(key, default)

try:
    import environ
    env = environ.Env(DEBUG=(bool, True), CHATBOT_ENABLED=(bool, True), CHATBOT_USE_OPENAI=(bool, False))
    if (BASE_DIR / '.env').exists():
        environ.Env.read_env(str(BASE_DIR / '.env'))
    _env = lambda k, d='': env(k, default=d)
except ImportError:
    pass

SECRET_KEY = _env('SECRET_KEY', 'django-insecure-change-this-in-production-abc123')
DEBUG = str(_env('DEBUG', 'True')).lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = [x.strip() for x in _env('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if x.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',
    'issues',
    'dashboard',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'campuscare.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'chatbot.context_processors.chatbot_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'campuscare.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile_redirect'
LOGOUT_REDIRECT_URL = 'accounts:home'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Email
EMAIL_BACKEND = _env('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = _env('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(_env('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = _env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = _env('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = _env('DEFAULT_FROM_EMAIL', 'CampusCare <noreply@campuscare.edu>')

# Chatbot
CHATBOT_ENABLED = _env('CHATBOT_ENABLED', 'True').lower() in ('true', '1', 'yes')
CHATBOT_USE_GEMINI = _env('CHATBOT_USE_GEMINI', 'True').lower() in ('true', '1', 'yes')
CHATBOT_USE_OPENAI = _env('CHATBOT_USE_OPENAI', 'False').lower() in ('true', '1', 'yes')
GEMINI_API_KEY = _env('GEMINI_API_KEY', '')
OPENAI_API_KEY = _env('OPENAI_API_KEY', '')

# File upload validation (5MB max)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
