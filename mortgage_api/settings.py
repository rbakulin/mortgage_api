import os
from datetime import timedelta

import environ

from .log_formatters import CustomJsonFormatter

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    environ.Env.read_env(env_path)

env = environ.Env()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY', default='not-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

if os.getenv('ENV') == 'prod':
    filepath = '/var/log/mortgage_api.log'
    backup_count = 30  # keep at most 30 log files on prod
    access_token_lifetime = timedelta(minutes=60)
else:
    filepath = os.path.join(BASE_DIR, 'mortgage_api.log')
    backup_count = 1
    access_token_lifetime = timedelta(days=1)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'drf_yasg',
    'corsheaders',

    'api',
    'mortgage',
    'authentication',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json_formatter': {
            '()': CustomJsonFormatter,
        },
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json_formatter',
            'filename': filepath,
            'backupCount': backup_count,
            'maxBytes': 5 * 1024 * 1024,  # 5MB
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

ROOT_URLCONF = 'mortgage_api.urls'

CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=True)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mortgage_api.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': access_token_lifetime,
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env.str('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': env.str('DATABASE_NAME', os.path.join(BASE_DIR, "db.sqlite3")),
        'USER': env.str('DATABASE_USER', ''),
        'PASSWORD': env.str('DATABASE_PASSWORD', ''),
        'HOST': env.str('DATABASE_HOST', ''),
        'PORT': env.str('DATABASE_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
