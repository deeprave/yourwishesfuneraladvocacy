# -*- coding: utf-8 -*-
"""
These are essentially overrides to the default django/wagtail configuration
Unfortunately this does not work for variables with dependencies in the
main configuration code.
"""
# import os
#
# PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = os.path.dirname(PROJECT_DIR)

# Override defaults


try:
    from .secrets import *
except ImportError:
    pass
