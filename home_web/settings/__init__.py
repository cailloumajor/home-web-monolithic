#-*- coding: utf-8 -*-

import os

from .development import *
from .external_config import yj_present

if os.environ.get('DJANGO_CONFIG_PARAM') == 'static_build': # pragma: no cover
    from .static_build import *
elif yj_present: # pragma: no cover
    from .production import *
