#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import dotenv

dotenv.load_dotenv('../.env')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ywfa.settings." + os.environ.get("DJANGO_MODE", "dev"))

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
