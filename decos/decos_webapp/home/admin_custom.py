# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description: Utility function to create or retrieve a Django Group representing a laboratory, distinguished by a custom 'laboratory' attribute, enabling synchronization with the Laboratories table in the PRP_CDM app.

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Project

def add_laboratory_group(lab_name):
    # Create or retrieve a Django Group with the provided lab_name
    new_group, created = Group.objects.get_or_create(name=lab_name)
    
    # Add custom attribute 'laboratory' to the group instance
    # This is expected to distinguish laboratory groups from other user roles
    if created:
        new_group.laboratory = True
        new_group.save()

    return new_group
