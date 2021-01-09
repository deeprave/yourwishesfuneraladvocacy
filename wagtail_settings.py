#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This python script edits a standard wagtail-generated site with opinionated settings
* read .env for project
* remove unnecessary files [Dockerfile, requirements.txt]
* replace [wa]sgi.py 
* override configuration
"""
import os
import dotenv

DEFAULTS = {
    'APP_DIR': 'app',
    'APP_NAME': 'app',
    'DJANGO_MODE': 'dev',
    'DJANGO_SECRET_KEY': '1a8ud%@_ge0s^lcwd681(0^q_xaxjm_k_4rn(3(2$!gchmaowr',
    'BASE_URL': 'http://example.com'
}


def var(name: str, default: str = None) -> str:
    if default is None:
        default = DEFAULTS[name]
    return os.environ.get(name, default)


dotenv.load_dotenv('.env')

app_dir = var('APP_DIR')
app_name = var('APP_NAME')
secret_key = var('DJANGO_SECRET_KEY')
base_url = var('BASE_URL')
django_mode = var('DJANGO_MODE')

app_root = os.path.join(app_dir, app_name)
settings_dir = os.path.join(app_root, 'settings')

settings_module = f'"{app_name}.settings." + os.environ.get("DJANGO_MODE", "dev")'


def edit_file_content(path: str, content: str, executable=False):
    with open(path, 'w') as fp:
        fp.write(content)
    if executable:
        os.chmod(path, 0o755)


edit_file_content(os.path.join(app_dir, 'pytest.ini'), f"""[pytest]
DJANGO_SETTINGS_MODULE = {app_name}.settings.{django_mode}
""")

# now, overwrite some files...
edit_file_content(os.path.join(app_dir, 'manage.py'), f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import dotenv

dotenv.load_dotenv('../.env')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", {settings_module})

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
""", executable=True)

edit_file_content(os.path.join(app_root, 'wsgi.py'), f"""# -*- coding: utf-8 -*-
# WSGI config for {app_name} project
import os
import dotenv

dotenv.load_dotenv('../.env')

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", {settings_module})

application = get_wsgi_application()
""")

edit_file_content(os.path.join(app_root, 'asgi.py'), f"""# -*- coding: utf-8 -*-
# ASGI config for {app_name} project
import os
import dotenv
from django.core.asgi import get_asgi_application

dotenv.load_dotenv('../.env')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", {settings_module})

application = get_asgi_application()
""")

edit_file_content(os.path.join(settings_dir, 'local.py'), f"""# -*- coding: utf-8 -*-
import os
import dj_database_url

# Override defaults

CACHES = {{
    "default" : {{
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ["REDIS_CACHE"],
        "OPTIONS": {{
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }}
    }},
    "sessions" : {{
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ["REDIS_SESSION"],
        "OPTIONS": {{
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }}
    }}
}}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

DATABASE_URL = os.environ['DATABASE_URL']

DATABASES = {{
    'default': dj_database_url.config(default=DATABASE_URL),
}}

WAGTAIL_SITE_NAME = '{app_name}'
BASE_URL = '{base_url}'

try:
    from .secrets import *
except ImportError:
    pass

""")

edit_file_content(os.path.join(settings_dir, 'secrets.py'), f"""# -*- coding: utf-8 -*-
SECRET_KEY = '{secret_key}'
""")

edit_file_content(os.path.join(settings_dir, '.gitignore'), "secrets.py\n")
