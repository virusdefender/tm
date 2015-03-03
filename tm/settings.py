# coding=utf-8
"""
Django settings for tm project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

import socket
import os
if socket.gethostname() == "MacBook-Pro.local":
    from .local_settings import *
else:
    from .server_settings import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!vtf0r_d^@ip%0yebdd1#o$hdlv)wtir=h$&qal#hg7^lec#1a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'DjangoUeditor',

    'xadmin',
    'crispy_forms',
    'account',
    'shop',
    'log',
    'utils',
    'signup',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'tm.urls'

WSGI_APPLICATION = 'tm.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'template'), )

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"), )

SESSION_COOKIE_AGE = 60 * 60 * 24 * 365 * 10

AUTH_USER_MODEL = 'account.User'

# redis config
SESSION_ENGINE = 'redis_sessions.session'

SESSION_REDIS_DB = 0

SHOPPING_CART_REDIS_DB = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}
        # 日志格式
    },
    'handlers': {
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH + 'error.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH + 'info.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'sms': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH + 'sms.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'pay': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH + 'pay.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        'info_logger': {
            'handlers': ['debug', "console"],
            'level': 'DEBUG',
            'propagate': True
        },
        'sms_logger': {
            'handlers': ['sms', "console"],
            'level': 'DEBUG',
            'propagate': True
        },
        'pay_logger': {
            'handlers': ['pay', "console"],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['console', 'debug'],
            'level': 'ERROR',
            'propagate': True,
        },
    },

}

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
TIME_FORMAT = 'H:i'