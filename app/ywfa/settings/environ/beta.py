from ..base import *
from .production import *

# identical to production, except the email backend

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages' # change this to a proper location

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '::1',
    '172.105.169.83',
    'beta.ywfa.com.au',
    'ywfa.com.au',
    'beta.yourwishesfuneraladvocacy.com.au',
    'yourwishesfuneraladvocacy.com.au',
]

BASE_URL = 'https://beta.yourwishesfuneraladvocacy.com.au'


TEMPLATE_LOADERS = [
    ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS)
]
