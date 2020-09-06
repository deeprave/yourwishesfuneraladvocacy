from .base import *
from .production import *

# identical to production, except the email backend

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages' # change this to a proper location

try:
    from .local import *
except ImportError:
    pass
