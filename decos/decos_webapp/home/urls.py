# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description: URL configuration for the Home app, defining endpoints for the user data entry interface and the laboratory switching functionality.

from django.urls import path
from .views import user_data_view, switch_lab_view

app_name = 'home'  # Namespace for the 'home' app URLs

urlpatterns = [
    # URL pattern for retrieving user data
    path('user-data/', user_data_view, name='user_data'),

    # URL pattern for switching between laboratories
    path('switch-laboratory/', switch_lab_view, name='switch-laboratory'),
]
