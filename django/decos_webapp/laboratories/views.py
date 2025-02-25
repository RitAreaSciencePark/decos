# Copyright (c) 2025 Marco Prenassi
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-25
# Description: 
# This module manages laboratory-related views in the PRP_CDM_app.
# It establishes a link between Django user roles (groups) and the Laboratories table 
# within the common data model, ensuring consistency and controlled access.

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from .forms import AddNewLabForm, ModifyLabForm
from django.contrib.auth.models import Group
from django.db.models import Model
from PRP_CDM_app.models.common_data_model import Laboratories
from django.contrib.auth.decorators import login_required, permission_required
import logging

# Logger setup for tracking operations and errors
logger = logging.getLogger(__name__)

# Handles the creation of new laboratory records and their associated user groups
@login_required
@permission_required('PRP_CDM_app.add_laboratories', raise_exception=True)
def AddLabView(request):
    if request.method == 'POST':
        form = AddNewLabForm(data=request.POST)
        if form.is_valid():
            lab_id = form.cleaned_data["lab_id"]
            try:
                # Check if a group with the given name already exists
                lab = Group.objects.get(name=lab_id)
            except Group.DoesNotExist:
                # Create a new group and mark it as a laboratory
                lab = Group(name=lab_id, laboratory=True)
                lab.save()

            # Save laboratory data
            form.save()
        else:
            errors = form.errors
            logger.warning(f"Lab creation failed: {errors}")
            return render(request, 'error_page.html', {'errors': errors})

    # Ensures consistency between the Groups marked as laboratories and the Laboratories table
    form = AddNewLabForm()
    if Group.objects.filter(laboratory=True).count() != Laboratories.objects.count():
        logger.error("Laboratories and Groups mismatch detected.")
        return render(request, 'error_page.html', {
            'errors': {'Group Mismatch': 'Laboratories and Groups are mismatched, contact an Administrator!'},
        })

    # Retrieve all laboratory records and render the form
    laboratories = list(Laboratories.objects.all())
    return render(request, 'laboratory_form.html', {'form': form, 'laboratories': laboratories})

# Handles updates to existing laboratory records
@login_required
@permission_required('PRP_CDM_app.change_laboratories', raise_exception=True)
def ModifyLabView(request, lab_id):
    if request.method == "POST":
        form = ModifyLabForm(data=request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.lab_id = lab_id
            data.save()
            return redirect("/admin/add-laboratory/")

    try:
        # Fetch the laboratory record by ID
        data = Laboratories.objects.get(pk=lab_id)
    except Laboratories.DoesNotExist:
        logger.error(f"Modification failed: Laboratory {lab_id} does not exist.")
        return render(request, 'error_page.html', {'errors': {'Lab Not Found': 'The specified lab does not exist.'}})

    # Render the modification form pre-filled with existing data
    form = ModifyLabForm(instance=data)
    return render(request, 'edit_laboratory_form.html', {'lab_name': lab_id, 'form': form})

# Handles the deletion of a laboratory record and its associated user group
@login_required
@permission_required('PRP_CDM_app.delete_laboratories', raise_exception=True)
def DeleteLabView(request, lab_id):
    if request.method == "POST":
        if request.POST.get('delete') == 'DELETE' and request.POST.get('security_question') == lab_id:
            try:
                # Fetch and delete the laboratory record
                lab_to_delete = Laboratories.objects.get(pk=lab_id)
                group_to_delete = Group.objects.get(name=lab_id, laboratory=True)

                lab_to_delete.delete()
                group_to_delete.delete()

                logger.info(f"Laboratory {lab_id} successfully deleted.")
                return redirect("/admin/add-laboratory/")
            except Laboratories.DoesNotExist:
                logger.error(f"Delete failed: Laboratory {lab_id} does not exist.")
                return render(request, 'error_page.html', {'errors': {'Lab Not Found': 'The specified lab does not exist.'}})
            except Group.DoesNotExist:
                logger.error(f"Delete failed: Group {lab_id} does not exist.")
                return render(request, 'error_page.html', {'errors': {'Group Not Found': 'Associated group does not exist.'}})

    try:
        # Fetch the laboratory record for confirmation before deletion
        data = Laboratories.objects.get(pk=lab_id)
    except Laboratories.DoesNotExist:
        logger.error(f"Delete failed: Laboratory {lab_id} not found.")
        return render(request, 'error_page.html', {'errors': {'Lab Not Found': 'The specified lab does not exist.'}})

    # Render the delete confirmation form
    return render(request, 'delete_laboratory_form.html', {'lab_name': lab_id})
