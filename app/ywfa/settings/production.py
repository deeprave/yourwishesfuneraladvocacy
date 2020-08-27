# noinspection PyUnresolvedReferences
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '::1', '172.105.169.83']

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

try:
    from .local import *
except ImportError:
    pass
