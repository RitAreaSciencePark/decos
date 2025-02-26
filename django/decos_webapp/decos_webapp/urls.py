# Copyright (c) 2025 Marco Prenassi
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description:
# URL configuration for the Home App in the DECOS Web Application.
# This module defines url routing for Django's admin interface, Wagtail's CMS, authentication via Allauth,
# document handling, and search functionality. .

from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from home.views import switch_lab_view
from search import views as search_views

urlpatterns = [
    # Django admin panel
    path("django-admin/", admin.site.urls),

    # Wagtail admin interface
    path("admin/", include(wagtailadmin_urls)),

    # Wagtail document serving
    path("documents/", include(wagtaildocs_urls)),

    # Custom search view
    path("search/", search_views.search, name="search"),
]

# Serve static and media files in development mode
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    # Django Allauth authentication URLs
    path("", include("allauth.urls")),

    # Include URLs from the home app with a namespace for proper URL resolution
    path("", include("home.urls", namespace="home")),

    # Catch-all routing for Wagtail pages, ensuring uncaptured paths are handled by Wagtail
    path("", include(wagtail_urls)),

    # Alternative: If Wagtail pages should be served from a subpath instead of the root
    # path("pages/", include(wagtail_urls)),
]
