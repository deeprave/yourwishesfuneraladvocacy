# -*- coding: utf-8 -*-
# WSGI config for ywfa project
import os
import dotenv

dotenv.load_dotenv('../.env')

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ywfa.settings." + os.environ.get("DJANGO_MODE", "dev"))

application = get_wsgi_application()
