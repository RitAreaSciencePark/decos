from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# This tells Django that HTTPS is being used even if a proxy (e.g., Nginx) handles it
SECURE_SSL_REDIRECT = True

# Define allowed domains for your application
ALLOWED_HOSTS = os.environ.get('DECOS_ALLOWED_HOSTS', 'localhost').split(',')
# Get WAGTAILADMIN_BASE_URL from environment variable
WAGTAILADMIN_BASE_URL = os.environ.get('WAGTAILADMIN_BASE_URL')

if not WAGTAILADMIN_BASE_URL:
    raise ValueError("WAGTAILADMIN_BASE_URL environment variable is not set")

# SECRET_KEY should always be read from an environment variable
SECRET_KEY = os.environ.get('DECOS_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DECOS_SECRET_KEY environment variable is not set")

CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
if not CSRF_TRUSTED_ORIGINS:
    raise ValueError("CSRF_TRUSTED_ORIGINS environment variable is not set")

# CSRF_TRUSTED_ORIGINS = ["https://10.128.8.14"]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static and media file locations
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Recommended static file URL paths
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
# print("media root: " + MEDIA_ROOT)

#print("static root: " + STATIC_ROOT)


STORAGES = {
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
}


# Add secure cookie settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

'''
# Add HSTS headers for HTTPS
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
'''

# Recommended logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}