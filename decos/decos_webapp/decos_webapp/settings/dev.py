from .base import *

print("I AM LOADED!")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# ADDED:
WAGTAILADMIN_BASE_URL = "http://10.128.8.14:8080"  # DEV DOMAIN

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-v^6bbtrnq64d&fp=%*@^@ix7si3_%^x@ova2k6&mj)w7tnlf9d"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

try:
    from .local import *
except ImportError:
    pass
WAGTAILADMIN_BASE_URL = "http://easydmp.localhost:8080"
WAGTAILADMIN_BASE_URL = "http://10.128.8.14:8080"
