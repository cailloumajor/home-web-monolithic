#-*- coding: utf-8 -*-

import os

# Minimal set of settings needed to build static files
STATIC_ROOT = os.environ.get('DJANGO_STATIC_BUILDDIR')
