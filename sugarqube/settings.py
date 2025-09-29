import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '.ngrok-free.app'
    ]
CSRF_TRUSTED_ORIGINS = ['https://acdd0b77dbcd.ngrok-free.app']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'ckeditor',
    # Local apps
    'users',
    'dashboard',
    'blog',
    'market',
    'trading_engine',
    'support',
    'notifications',
    'debug_toolbar',  # Added for debugging
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.KYCVerificationMiddleware',    
]

ROOT_URLCONF = 'sugarqube.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sugarqube.context_processors.currency_context', # Added context processor
            ],
        },
    },
]

WSGI_APPLICATION = 'sugarqube.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# sugarqube/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'SugarQubeDB',
        'USER': 'neondb_owner',
        'PASSWORD': 'npg_iQS1dGb0rtcL',
        'HOST': 'ep-icy-salad-a14fbso3.ap-southeast-1.aws.neon.tech', # Unpooled host
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
            'options': '-c search_path=public'
        },
    },
    'credentials': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'SugarQubeDB',
        'USER': 'neondb_owner',
        'PASSWORD': 'npg_iQS1dGb0rtcL',
        'HOST': 'ep-icy-salad-a14fbso3.ap-southeast-1.aws.neon.tech', # Unpooled host
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
            'options': '-c search_path=credentials,public'
        },
    },
    'sugarprices': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'SugarQubeDB',
        'USER': 'neondb_owner',
        'PASSWORD': 'npg_iQS1dGb0rtcL',
        'HOST': 'ep-icy-salad-a14fbso3.ap-southeast-1.aws.neon.tech', # Unpooled host
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
            'options': '-c search_path=sugarprices,public'
        },
    }
}

DATABASE_ROUTERS = [
    'sugarqube.credentials_router.CredentialsRouter',
    'sugarqube.sugarprices_router.SugarPricesRouter',
    'sugarqube.public_router.PublicRouter',
]

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

# CKEditor Configuration
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 800,
    },
}

# Email Configuration (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # For development

# Authentication redirects
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'  # This will send users to landing page after logout
LOGIN_URL = '/accounts/login/'

INTERNAL_IPS = [
    '127.0.0.1',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

