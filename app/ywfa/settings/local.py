# -*- coding: utf-8 -*-
"""
These are essentially overrides to the default django/wagtail configuration
Unfortunately this does not work for variables with dependencies in the
main configuration code.
"""
import os
import dj_database_url

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Override defaults

CACHES = {
    "default" : {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ["REDIS_CACHE"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    },
    "sessions" : {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ["REDIS_SESSION"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

DATABASE_URL = os.environ['DATABASE_URL']

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL),
}

WAGTAIL_SITE_NAME = 'Your Wishes Funeral Advocacy'
BASE_URL = 'https://yourwishesfuneraladvocacy.com.au'

TIME_ZONE = 'Australia/Melbourne'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
    'sass_processor.finders.CssFinder',
]

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(BASE_DIR, 'node_modules')
]

NPM_ROOT_PATH = BASE_DIR
NPM_STATIC_FILES_PREFIX = 'vendor'
NPM_FILE_PATTERNS = {
    'bootstrap': [
        'dist/css/bootstrap.min.css',
        'dist/js/bootstrap.min.js'
    ],
    'popper.js': [
        'dist/umd/popper.min.js'
    ],
}

try:
    from .secrets import *
except ImportError:
    pass

