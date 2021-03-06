#-*- coding: utf-8 -*-

from .external_config import yjval

SECRET_KEY = yjval('secret_key')

ADMINS = tuple(tuple(x) for x in yjval('admins'))

EMAIL_HOST = yjval('email.host')
EMAIL_PORT = yjval('email.port')
EMAIL_HOST_PASSWORD = yjval('email.pass')
EMAIL_HOST_USER = yjval('email.user')
EMAIL_USE_TLS = yjval('email.tls')

ALLOWED_HOSTS = yjval('allowed_hosts')

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': yjval('db.name'),
        'USER': yjval('db.user'),
        'PASSWORD': yjval('db.pass'),
        'HOST': yjval('db.host'),
        'PORT': yjval('db.port'),
    }
}

STATIC_ROOT = yjval('static_root')

REQUIREJS_PROD = True

PILOTWIRE_CONTROLER = {
    'address': yjval('pilotwire.address'),
    'port': yjval('pilotwire.port'),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'rq_console': {
            'format': "%(asctime)s %(message)s",
            'datefmt': "%Y.%m.%d %H:%M:%S",
        },
    },
    'handlers': {
        'pilotwire': {
            'level': 'INFO',
            'class': 'heating.log.PilotwireHandler',
            'logLength': 500,
        },
        'rq_console': {
            'level': 'INFO',
            'class': 'rq.utils.ColorizingStreamHandler',
            'formatter': 'rq_console',
        },
    },
    'loggers': {
        'setpilotwire': {
            'handlers': ['pilotwire'],
            'level': 'INFO',
        },
        'rq.worker': {
            'handlers': ['rq_console'],
            'level': 'INFO',
        },
    },
}

RQ_ACTIVE = True

RQ_QUEUES = {
    'default': yjval('rq_queue')
}
