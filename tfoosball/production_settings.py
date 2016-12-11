from tfoosball.common_settings import *
import os
import dj_database_url


SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = os.environ.get('DJANGO_DEBUG', False)
ALLOWED_HOSTS = [
    'tfoosball-api.herokuapp.com',
    'tfoosball.herokuapp.com',
]

CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
