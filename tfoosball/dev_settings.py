from tfoosball.common_settings import *  # NOQA
from tfoosball.common_settings import BASE_DIR
import os


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7d!g5l*3nm1=2s@&%11d+jz_$#ii2bugj+9ynhq&cfl0r%pnn)'
DEBUG = True
ALLOWED_HOSTS = [
    'localhost',
]

# DATABASE
# ------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# CORS
# ------------------------------------------------------------------------------
CORS_ORIGIN_WHITELIST = (
    'localhost:8000',
    'localhost:3000',
)

# LOGGING
# ------------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'matches.log'), # NOQA
            'formatter': 'verbose'
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'tfoosball.matches': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        }
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'emails.log')
