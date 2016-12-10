from tfoosball.common_settings import *
import os
import dj_database_url


SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = [
    'tfoosball-api.herokuapp.com',
    'tfoosball.herokuapp.com',
]

CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

DATABASES = {
    'default': dj_database_url.config()
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
