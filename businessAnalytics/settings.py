'''
Author: Saijal Shakya
Development:
    > LMS: December 20, 2018
    > HRM: Febraury 15, 2019
    > CRM: March, 2020
    > Inventory Sys: April, 2020
    > Analytics: ...
License: Credited
Contact: https://saijalshakya.com.np
'''
import os
import yaml
credentials = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = credentials['secret_key']
DEBUG = credentials['debug']

ALLOWED_HOSTS = credentials['allowed_host']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'ckeditor',
    'ckeditor_uploader',
    'services',
    'inventory',
    'leave_manager',
    'employee',
    'lms_user',
    'sysManager',
    'crmManager',
    'support',
    'hrm',
]

CKEDITOR_UPLOAD_PATH = "uploads/"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

ROOT_URLCONF = 'businessAnalytics.urls'

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
                'crmManager.context_processor.common',
            ],
        },
    },
]

WSGI_APPLICATION = 'businessAnalytics.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': credentials['db_engine'],
        'NAME': credentials['db_name'],
        'USER': credentials['db_user'],
        'PASSWORD': credentials['db_password'],
        'PORT': credentials['db_port']
    }
}

CACHES = {
    "default": {
        "BACKEND": credentials['cache_backend'],
        "LOCATION": credentials['cache_location'],
        "OPTIONS": {
            "CLIENT_CLASS": credentials['client_class']
        },
        "KEY_PREFIX": credentials['key_prefix']
    }
}

CACHE_TTL = 60 * 1

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

LANGUAGE_CODE = 'en-us'
LOGIN_URL = "/login"
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media'
STATICFILES_DIRS = [BASE_DIR+"/assets", ]
STATIC_ROOT = BASE_DIR+'/static'
MEDIA_ROOT = BASE_DIR+'/media'
MEDIA_URL = '/media/'

EMAIL_USE_TLS = credentials['EMAIL_USE_TLS']
EMAIL_HOST = credentials['smtp_server']
EMAIL_HOST_USER = credentials['_email']
EMAIL_HOST_PASSWORD = credentials['_password']
EMAIL_PORT = credentials['smtp_port']
EMAIL_USE_SSL = credentials['EMAIL_USE_SSL']
