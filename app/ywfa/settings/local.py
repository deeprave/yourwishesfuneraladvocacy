# -*- coding: utf-8 -*-
import os
import dj_database_url

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

WAGTAIL_SITE_NAME = 'ywfa'
BASE_URL = 'https://yourwishesfuneraladvocacy.com.au'

try:
    from .secrets import *
except ImportError:
    pass

