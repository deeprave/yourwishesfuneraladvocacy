"""
Django settings for ywfa project.
"""
from pathlib import Path
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
# noinspection PyPackageRequirements
from django_env import Env

# noinspection PyUnresolvedReferences
from .logger import *

SETTINGS_DIR = Path(__file__).resolve().parent.parent
DJANGO_ROOT = SETTINGS_DIR.parent
PROJECT_ROOT = DJANGO_ROOT.parent

env = Env(exception=ImproperlyConfigured)
if env.bool('DJANGO_READ_DOT_ENV_FILE', default=False):
    env.read_env(search_path=DJANGO_ROOT, parents=True)

DEBUG = env.bool('DJANGO_DEBUG', False)
SECRET_KEY = env['DJANGO_SECRET_KEY']

# Application definition

LOCAL_APPS = [
    'cms',
    'cms_blocks',
    'testimonials',
    'contact',
    'ywfa_settings',

    'shop',
]

WAGTAIL_APPS = [
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.table_block',
    'wagtail.contrib.settings',
    'wagtail.contrib.sitemaps',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'modelcluster',
    'taggit',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'wagtailmenus',

    'storages',

    'widget_tweaks',
    'django_extensions',

    'django_sass',
    'compressor',
    'crispy_forms',
]

INSTALLED_APPS = LOCAL_APPS + \
    WAGTAIL_APPS + \
    DJANGO_APPS + \
    THIRD_PARTY_APPS


MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'ywfa.urls'

TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            DJANGO_ROOT / 'templates',
        ],
        'OPTIONS': {
            'loaders': TEMPLATE_LOADERS,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
                'wagtailmenus.context_processors.wagtailmenus',
                'shop.context_processors.cart',
            ],
        },
    },
]



WSGI_APPLICATION = 'ywfa.wsgi.application'

DATABASES = {
    'default': env.database_url(),
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = env.get('DJANGO_LANG', 'en-us')
TIME_ZONE = env.get('DJANGO_TZ', 'Australia/Melbourne')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Wagtail settings

WAGTAIL_SITE_NAME = 'Your Wishes Funeral Advocacy'
BASE_URL = 'https://yourwishesfuneraladvocacy.com.au'
WAGTAILIMAGES_MAX_UPLOAD_SIZE = env.int('MAX_UPLOAD_SIZE', 20 * 1024 * 1024)  # i.e. 20MB
WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = env.get('EMAIL_FROM', 'webmaster@ywfa.com.au')
WAGTAILADMIN_NOTIFICATION_USE_HTML = True
WAGTAILADMIN_NOTIFICATION_INCLUDE_SUPERUSERS = False
WAGTAIL_ENABLE_UPDATE_CHECK = True
WAGTAIL_USAGE_COUNT_ENABLED = True

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash

CACHES = {
    "default": env.cache_url(),
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = 'default'

# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
    'compressor.finders.CompressorFinder',
]

def path_slash(path):
    """with a trailing slash"""
    return f"{path}/"

STATIC_URL = '/static/'
STATIC_ROOT = path_slash(DJANGO_ROOT / 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = path_slash(DJANGO_ROOT / 'media')

# django-npm settings

NPM_ROOT_PATH = DJANGO_ROOT
NPM_STATIC_FILES_PREFIX = ''
NPM_FINDER_USE_CACHE = True
NPM_FILE_PATTERNS = {
    'bootstrap-icons': [
        'bootstrap-icons.svg',
        'icons/*',
    ],
    '@popperjs': [
        'core/dist/umd/popper.js',
        'core/dist/umd/popper.js.map',
    ],
    'bootstrap': [
        'dist/js/bootstrap.js',
        'dist/js/bootstrap.js.map',
    ],
    'socicon': [
        'css/socicon.css',
        'font/*',
    ]
}

# django-compress settings
COMPRESS_ENABLED = True
COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_FILTERS = {
    'css': [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSCompressorFilter',
    ],
    'js': [
        'compressor.filters.jsmin.CalmjsFilter',
    ]
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

CART_SESSION_ID = '_ywfa_cart'
ORDER_SESSION_ID = '_ywfa_order'

STRIPE_PUBLIC_KEY = env['STRIPE_PUBLIC_KEY']
STRIPE_PRIVATE_KEY = env['STRIPE_PRIVATE_KEY']
STRIPE_SIGNING_KEY = env['STRIPE_SIGNING_KEY']


# media files handling

if env.is_all_set('S3_ACCESS_KEY', 'S3_SECRET_KEY', 'S3_BUCKET_NAME', 'S3_REGION'):
    AWS_ACCESS_KEY_ID = AWS_S3_ACCESS_KEY_ID = env['S3_ACCESS_KEY']
    AWS_SECRET_ACCESS_KEY = AWS_S3_SECRET_ACCESS_KEY = env['S3_SECRET_KEY']
    AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME = env['S3_BUCKET_NAME'], env['S3_REGION']
    AWS_S3_DOMAIN = env.get('S3_DOMAIN', 'linodeobjects.com')
    AWS_S3_USE_SSL = True

    AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_REGION_NAME}.{AWS_S3_DOMAIN}"

    MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


DJANGO_TOOLBAR_ENABLED = DEBUG and env.bool('DJANGO_TOOLBAR_ENABLED', False)
