from .base import *

DEBUG = False
# ADDED:
WAGTAILADMIN_BASE_URL = "http://10.128.8.14:8080"  # or your production domain
try:
    from .local import *
except ImportError:
    pass
