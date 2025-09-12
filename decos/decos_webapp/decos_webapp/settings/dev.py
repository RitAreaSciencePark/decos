"""
Django settings for the development environment.

Notes
- Inherits common defaults from `base.py` and then applies development-friendly
  overrides (e.g., `DEBUG=True`, permissive hosts, console email backend).
- Do NOT use this file for production. Create a separate `prod.py` and keep
  sensitive values in environment variables or a secrets manager.
"""

from .base import *
import os

# Debug mode: enables verbose error pages and disables several prod-only checks.
# SECURITY WARNING: Never enable DEBUG in production.
DEBUG = True

# Base URL used by Wagtail for things like previews and notifications in admin.
# In dev, this can point to your local or sandbox environment.
# Read from env var `WAGTAILADMIN_BASE_URL`, falling back to current dev default.
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL", "http://10.128.8.14:8080")

# Secret key used for cryptographic signing (sessions, CSRF, etc.).
# OK to hardcode for local development, but NEVER hardcode or reuse in prod.
# Secret read
from pathlib import Path
path = Path("/app/",os.getenv("DECOS_SECRET_KEY_HOST_FILE"))
with path.open("r", encoding="utf-8") as f:
    SECRET_KEY = f.read().strip()

# Hostnames the app will serve. In development, `*` is convenient.
# In production, restrict this to explicit hostnames/domains.
ALLOWED_HOSTS = ["*"]

# Route emails to the console in development so no real emails are sent.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Optionally allow machine-specific overrides in `local.py` (gitignored).
# Useful for developers to tweak settings without affecting the shared repo.
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
