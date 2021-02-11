"""
Django settings for ywfa project.
"""
from pathlib import Path
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django_env import Env

# noinspection PyUnresolvedReferences
from .logger import *

SETTINGS_DIR = Path(__file__).resolve().parent.parent
DJANGO_ROOT = SETTINGS_DIR.parent
PROJECT_ROOT = DJANGO_ROOT.parent

env = Env(exception=ImproperlyConfigured)
if env.bool('DJANGO_READ_DOT_ENV_FILE', default=False):
    env.read_env(search_path=PROJECT_ROOT, parents=True)


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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            DJANGO_ROOT / 'templates',
        ],
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader'
                ])
            ],
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
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
    'compressor.finders.CompressorFinder',
]
STATICFILES_DIRS = [
    DJANGO_ROOT / 'static',
]
STATIC_ROOT = DJANGO_ROOT / 'staticfiles'
STATIC_URL = '/static/'
MEDIA_ROOT = DJANGO_ROOT / 'media'
MEDIA_URL = '/media/'

# django-npm settings

NPM_ROOT_PATH = DJANGO_ROOT
NPM_STATIC_FILES_PREFIX = ''
NPM_FINDER_USE_CACHE = True
NPM_FILE_PATTERNS = {
    'bootstrap-icons': [
        'bootstrap-icons.svg',
        'icons/*',
    ],
    'popper.js': [
        'dist/umd/popper.js',
        'dist/umd/popper.js.map',
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

CART_SESSION_ID = '_ywfa_cart'
ORDER_SESSION_ID = '_ywfa_order'
CRISPY_TEMPLATE_PACK = 'bootstrap4'
STRIPE_PUBLIC_KEY = env['STRIPE_PUBLIC_KEY']
STRIPE_PRIVATE_KEY = env['STRIPE_PRIVATE_KEY']
