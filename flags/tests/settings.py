from __future__ import absolute_import, unicode_literals

import os

import django


SECRET_KEY = 'not needed'

django.setup()

DATABASES = {
    'default': {
        'ENGINE': os.environ.get(
            'DATABASE_ENGINE',
            'django.db.backends.sqlite3'
        ),
        'NAME': os.environ.get('DATABASE_NAME', 'flags'),
        'USER': os.environ.get('DATABASE_USER', None),
        'PASSWORD': os.environ.get('DATABASE_PASS', None),
        'HOST': os.environ.get('DATABASE_HOST', None),

        'TEST': {
            'NAME': os.environ.get('DATABASE_NAME', None),
        },
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'wagtail.wagtailcore',
    'flags',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]
