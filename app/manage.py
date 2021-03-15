#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from django_env import Env


if __name__ == "__main__":
    env = Env()
    env.setdefault("DJANGO_SETTINGS_MODULE", "ywfa.settings.environ." + env.get("DJANGO_MODE", "production"))

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
