# -*- coding: utf-8 -*-
# ASGI config for ywfa project
import os
import dotenv
from django.core.asgi import get_asgi_application

dotenv.load_dotenv('../.env')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ywfa.settings." + os.environ.get("DJANGO_MODE", "dev"))

application = get_asgi_application()
