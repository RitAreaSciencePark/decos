# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description: URL configuration for the Home app, defining endpoints for the user data entry interface and the laboratory switching functionality.

from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .views import user_data_view, switch_lab_view, delete_sample_entry, delete_experiment_dmp_entry, delete_result_entry, get_epiro_data

def in_data_curator_group(user):
    return user.groups.filter(name="Data_Curator").exists()

app_name = 'home'  # Namespace for the 'home' app URLs

urlpatterns = [
    # URL pattern for retrieving user data
    path('user-data/', user_data_view, name='user_data'),

    # URL pattern for switching between laboratories
    path('switch-laboratory/', switch_lab_view, name='switch-laboratory'),

    # URL pattern for deleting a sample entry
    path(
        'delete-sample-entry/',
        login_required(user_passes_test(in_data_curator_group)(require_POST(delete_sample_entry))),
        name='delete_sample_entry'
    ),

    # URL pattern for deleting a experiment dmp entry
    path(
        'delete-experiment-dmp-entry/',
        login_required(user_passes_test(in_data_curator_group)(require_POST(delete_experiment_dmp_entry))),
        name='delete_experiment_dmp_entry'
    ),

    #URL pattern for deleting a result entry
    path(
        'delete-result-entry/',
        login_required(user_passes_test(in_data_curator_group)(require_POST(delete_result_entry))),
        name='delete_result_entry'
    ),

    #URL pattern to update from EPIRO
    path(
        'epiro-update/',
        login_required(get_epiro_data),
        name='epiro-update'
    )
]
