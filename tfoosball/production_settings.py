from tfoosball.common_settings import * # NOQA
import os
import dj_database_url


SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = os.environ.get('DJANGO_DEBUG', False)
DEBUG = True if DEBUG == 'True' else DEBUG

ALLOWED_HOSTS = [
    'tfoosball-api.herokuapp.com',
    'tfoosball.herokuapp.com',
]

CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
}

# CORS
# ------------------------------------------------------------------------------

CORS_ORIGIN_WHITELIST = (
    'tfoosball-api.herokuapp.com',
    'tfoosball.herokuapp.com',
)

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# EMAIL SERVER CONFIG
# ------------------------------------------------------------------------------
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
EMAIL_PORT = 587
EMAIL_USE_TLS = True
