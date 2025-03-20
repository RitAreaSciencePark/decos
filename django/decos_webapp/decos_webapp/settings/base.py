# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# 
# Description: 
# This file contains the base settings for the Django Wagtail project 'decos_webapp'. 
# It defines the core configurations, including installed applications, middleware, 
# database connections, authentication settings, static file management, and Wagtail-specific settings.

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import django

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/


# Application definition
INSTALLED_APPS = [
    "home",  # Main application for the web interface
    "search",  # Implements search functionality within the project
    "wagtail.contrib.forms",  # Enables form handling in Wagtail
    "wagtail.contrib.redirects",  # Manages URL redirects within Wagtail
    "wagtail.embeds",  # Supports embedding external content
    "wagtail.sites",  # Handles multi-site management in Wagtail
    "wagtail.users",  # User management integration for Wagtail admin
    "wagtail.snippets",  # Enables reusable content snippets
    "wagtail.documents",  # Manages document uploads and organization
    "wagtail.images",  # Provides image management capabilities
    "wagtail.search",  # Configures search backends for Wagtail
    "wagtail.admin",  # Wagtail's administrative interface
    "wagtail",  # Core Wagtail CMS framework
    "modelcluster",  # Dependency for managing relationships in Wagtail models
    "taggit",  # Implements tagging functionality for content classification
    "django.contrib.admin",  # Django's built-in admin interface
    "django.contrib.auth",  # Authentication and user management
    "django.contrib.contenttypes",  # Framework for generic model relations
    "django.contrib.sessions",  # Session management
    "django.contrib.messages",  # Messaging framework for user notifications
    "django.contrib.staticfiles",  # Manages static file handling
    "wagtail.contrib.settings",  # Site-wide configurable settings in Wagtail
    "django.forms",  # Enables form customization and rendering
    "PRP_CDM_app",  # Custom app supporting the PRP@CERIC common data model 
    "allauth",  # Third-party authentication system
    "allauth.account",  # Account authentication and registration
    "allauth.socialaccount",  # Social authentication integration
    "allauth.socialaccount.providers.openid_connect",  # OpenID Connect support
    "django_tables2",  # Table rendering framework for structured data display
    "laboratories",  # Custom application for laboratories and groups/role linking
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",  # Manages user sessions using the configured session backend
    "django.middleware.common.CommonMiddleware",  # Provides essential HTTP functionalities like URL rewriting and content-length headers
    "django.middleware.csrf.CsrfViewMiddleware",  # Protects against Cross-Site Request Forgery (CSRF) attacks
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Associates users with requests, enabling authentication and permissions
    "django.contrib.messages.middleware.MessageMiddleware",  # Supports temporary messages across requests (e.g., success/error notifications)
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Prevents clickjacking attacks by controlling the X-Frame-Options header
    "django.middleware.security.SecurityMiddleware",  # Enhances security by enabling protections like HSTS, XSS filtering, and SSL redirection
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",  # Handles page redirects within Wagtail to ensure smooth navigation
    "allauth.account.middleware.AccountMiddleware",  # Middleware to manage account-related session behaviors for Django Allauth
]

ROOT_URLCONF = "decos_webapp.urls"  # Specifies the main URL configuration file for request routing

ACCOUNT_FORMS = {
    'signup': 'home.auth.UserRegistrationForm',  # Custom registration form for user sign-up, replacing the default Allauth form
    'login': 'home.auth.UserLoginForm',  # Custom login form to modify authentication behavior and user validation
}
from django.forms.renderers import TemplatesSetting

class CustomFormRenderer(TemplatesSetting):
    # NOTE: The author is not sure if this custom form renderer is working correctly.
    # Overrides the default Django form renderer with custom templates for form structure and field rendering.
    form_template_name= "decos_webapp/forms/div.html"  # Defines the structure for rendering entire forms.
    field_template_name = "decos_webapp/forms/field.html"  # Specifies how individual form fields are displayed.

# Sets the custom form renderer globally for all Django forms.
FORM_RENDERER = "decos_webapp.settings.base.CustomFormRenderer"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",  # Uses Django's built-in template engine.
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),  # Main template directory for the project.
            os.path.join(PROJECT_DIR, "templates/widgets"),  # Contains custom widget templates.
            # django.__path__[0] + "/forms/templates",  # Commented-out alternative template path.
            os.path.join("/app/django/django","forms/templates"),  # Custom template path for form rendering.
        ],
        "APP_DIRS": True,  # Enables automatic discovery of templates within installed apps.
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",  # Provides debug-related context variables.
                "django.template.context_processors.request",  # Adds the `request` object to templates.
                "django.contrib.auth.context_processors.auth",  # Includes authentication-related context.
                "django.contrib.messages.context_processors.messages",  # Enables Django’s messaging framework.
                "wagtail.contrib.settings.context_processors.settings",  # Makes Wagtail site settings available in templates.
            ],
        },
    },
]
WSGI_APPLICATION = "decos_webapp.wsgi.application"  # Entry point for WSGI servers to run the Django application.

# DATABASE ROUTING: crucial for handling multiple databases, ensures queries are directed correctly.
DATABASE_ROUTERS = ["decos_webapp.db_routers.ExternalDbRouter"]  # Custom database router located in db_routers.py.

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL database engine.
        'NAME': 'decos_webapp_db',  # Main database for storing application data.
        'USER': 'decos',  # Database username.
        'PASSWORD': 'postgres', # FIXME: Update with a secure password before deployment.
        'HOST': 'db',  # Database server hostname.
        'PORT': '5432',  # Default PostgreSQL port.
    },
    "prpmetadata-db": {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL database engine for metadata storage.
        'NAME': 'decos_metadata_db',  # Database storing metadata for the PRP system.
        'USER': 'decos',  # Database username.
        'PASSWORD': 'postgres', # FIXME: Update with a secure password before deployment.
        'HOST': 'db',  # Database server hostname.
        'PORT': '5432',  # Default PostgreSQL port.
    }
}


# Static and media file settings

# Defines how Django locates static files across the project.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",  # Looks for static files in STATICFILES_DIRS.
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",  # Finds static files within each installed app’s 'static/' folder.
]

# Additional directories for static files outside of installed apps.
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),  # Includes a project-wide 'static/' directory.
]

# Directory where Django collects all static files when running collectstatic (used in production).
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# URL prefix for accessing static files in development and production.
STATIC_URL = "/static/"
# Directory where uploaded media files (e.g., user images, documents) are stored.
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Base URL for serving media files (used in development; in production, a web server should handle this).
MEDIA_URL = "/media/"

# Default storage settings, with improved handling for static files.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",  # Stores uploaded media files in the local filesystem.
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",  
        # Ensures static file names include a hash for cache busting (recommended for production).
    },
}


# Wagtail settings
WAGTAIL_SITE_NAME = "decos_webapp"

# Search backend for Wagtail
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Wagtail document upload restrictions
WAGTAILDOCS_EXTENSIONS = ['csv', 'docx', 'key', 'odt', 'pdf', 'pptx', 'rtf', 'txt', 'xlsx', 'zip']

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# HIC SUNT LEONES:
# Allauth authentication settings
SITE_ID = 1

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
# ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_LOGIN_METHODS = {'email', 'username'}

ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/login/'
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_BLACKLIST = ["admin", "god"]
ACCOUNT_USERNAME_MIN_LENGTH = 2

# OpenID Connect authentication via Allauth



SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "SERVERS": [
            {
                "id": "authentik",
                "name": "Authentik",
                "server_url": "https://orfeo-auth.areasciencepark.it/application/o/deocs/.well-known/openid-configuration",
                "token_auth_method": "client_secret_basic",
                "APP": {
                    "client_id": "p0d4fDR25PIXsnbaDFxq38xIzVhua5WjGdlwAi1N",
                    "secret": "W87tnfhqdsI8uz5pAdkcZbiIDv23ZBCvbH2FtWEYzH8vJAX7XnfZJhcJRnnl1XAQyHXeq9Mt2cObTsp5p9l6akQMNLiUtXAM3HVdtSjVEphy6gHq2oK8gJsf90u1Yd9e"
                },
            }
        ]
    }
}
