# -*- coding: utf-8 -*-
# WSGI config for ywfa project
from os import environ as env

from django.core.wsgi import get_wsgi_application


env.setdefault("DJANGO_SETTINGS_MODULE", "ywfa.settings.environ." + env.get("DJANGO_MODE", "dev"))
application = get_wsgi_application()
