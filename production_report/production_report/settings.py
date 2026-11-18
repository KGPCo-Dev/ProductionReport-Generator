"""
Django settings for production_report project.
Optimized for multi-container deployment (Apache + Gunicorn)
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Get variables from .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# Enviroment and Security settings (HARDENING)
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-^xtffyt0m#ptf63))fiq6^d0#=v(96s^-%b&mkne(0tzd#p69-')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '10.50.60.171',
    '172.26.60.62',
    os.getenv('DJANGO_ALLOWED_HOST', 'tu-app.kgpco.com')
]

INTERNAL_IPS = [
    "127.0.0.1",
]

if not DEBUG:
    X_FRAME_OPTIONS = 'DENY'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Solo forzar SSL si estamos en un entorno de producción real (no en runserver)
    # Esta variable la estableceremos en nuestro entorno de despliegue (ej. Docker/Podman)
    if os.getenv('DJANGO_ENV') == 'production':
        SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host != 'localhost']

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Development tools
    'django_bootstrap5',
    'rest_framework',
    'rest_framework.authtoken',
    
    # Local apps
    'reports',
    'home',
    'order_tracker',
    'live_dashboards',
    'cutting_machine_assignation',
    'agent',
    
    # Autenticación Microsoft Entra ID (Allauth)
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.microsoft',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "allauth.account.middleware.AccountMiddleware", # django-allauth required
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'production_report.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request', # django-allauth required
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'production_report.wsgi.application'

# ==============================================================================
# DATABASE CONFIGURATION (SUPABASE / POSTGRES)
# ==============================================================================

DATABASES = {
    'default': dj_database_url.config( 
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================================
# INTERNATIONALIZATION (MÉXICO)
# ==============================================================================

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Monterrey'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC AND MEDIA FILES MANAGEMENT
# ==============================================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# ==============================================================================

REST_FRAMEWORK = { 
    'DEFAULT_AUTHENTICATION_CLASSES': [ 
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [ 
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ==============================================================================
# DJANGO-ALLAUTH & MICROSOFT ENTRA ID CONFIGURATION
# ==============================================================================

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'none'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'microsoft': {
        'APP': {
            'client_id': os.getenv('AZURE_LOGIN_CLIENT_ID'),
            'secret': os.getenv('AZURE_LOGIN_SECRET_VALUE'),
            'key': '',
        },
        'TENANT': os.getenv('AZURE_LOGIN_CLIENT_TENANT', 'common'),
    }
}

LOGIN_URL = 'accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_LOGIN_ON_GET = True