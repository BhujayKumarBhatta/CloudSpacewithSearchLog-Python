"""
Django settings for djp1 project.

Generated by 'django-admin startproject' using Django 1.10rc1.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$hrr=iim80@a()4$&*k$yk5r+a_l+8an$su2@3@0xh6t6=_lib'

# SECURITY WARNING: don't run with debug turned on in production!
# Celery settings

CELERY_BROKER_URL = 'amqp://guest:guest@localhost//'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
#CELERY_RESULT_BACKEND = 'rpc://'
#CELERY_RESULT_BACKEND ='amqp://'
CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'
#CELERY_RESULT_BACKEND='celery.backends.database:DatabaseBackend'
CELERY_RESULT_PERSISTENT = True
#CELERY_RESULT_BACKEND = 'cache'
#CELERY_CACHE_BACKEND = 'memory'
CELERY_TASK_SERIALIZER = 'json'
#CELERY_RESULT_SERIALIZER = 'pickle' # without this it was showing the resultserver is query result type 
                                    # and hence it was not JSON serializable
#CELERY_RESULT_SERIALIZER='json'
#CELERY_TASK_RESULT_EXPIRES = 18000
CELERY_IMPORTS = ('app1.views') # otherwise  task is only getting loaded from tasks.py 

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app1',
    #'celery',
    'djp1.celery',
    'djcelery',
    'rest_framework'
]

MIDDLEWARE_CLASSES = [    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',       
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djp1.urls'

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

WSGI_APPLICATION = 'djp1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE':'sql_server.pyodbc',
#        'NAME':'searchlog',
#        'HOST':'MSSQL1',
#        'PORT':'9000',
#        'USER':'mssql',
#        'PASSWORD':'mysql123'
#    }
#}

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME':'searchlog',
        'HOST':'mysqldb-server1',
        'PORT':'3306',
        'USER':'mysql',
        'PASSWORD':'mysql123'
    }
}


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'
TIME_ZONE =  'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'   # what happens for  after sucessful login what happens
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'Domain <noreplay@example.com>'

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
    
}

