#-*- coding: utf-8 -*-

import os

# Minimal set of settings needed to build static files with require application
STATIC_ROOT = os.environ.get('DJANGO_STATIC_BUILDDIR')
STATICFILES_STORAGE = 'require.storage.OptimizedStaticFilesStorage'
