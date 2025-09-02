# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description: View functions for the Home app, enabling laboratory switching and user data management, including API token handling, within the DECOS experiment metadata catalog system.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import (
    LabSwitchForm,
    UserDataForm,
    APITokenForm,
)
from PRP_CDM_app.models.common_data_model import (
    Users,
    Laboratories,
)

from django.views.decorators.http import require_POST
from django.contrib import messages
from PRP_CDM_app.models.common_data_model import Samples, Results
from .secrets_models import API_Tokens

# Functional view for switching between laboratories.
@login_required
def switch_lab_view(request):
    # Ensure the user is authenticated before proceeding
    if request.user.is_authenticated:
        username = request.user.username
    user_labs=request.user.groups.filter(laboratory=True)
    if request.method == 'POST':
        # Handle form submission for laboratory selection
        form = LabSwitchForm(data=request.POST, user_labs=user_labs)
        if form.is_valid():
            # Store the selected laboratory in the session
            laboratory = form.cleaned_data.get('lab_selected')
            request.session["lab_selected"] = laboratory
            try:
                # Redirect the user to the previously stored page
                return redirect(request.session["return_page"])
            except KeyError:
                # Fallback to the homepage if no return page is available
                return redirect('/')
    else:
        # Store the referring page to enable returning to it after switching
        try:
            request.session["return_page"] = request.META['HTTP_REFERER']
        except KeyError:
            request.session["return_page"] = "/"

        # Verify if the user is assigned to any laboratory
        if not request.user.groups.all():
            return render(request, 'home/error_page.html', {
                'errors': {"No assigned laboratory": "Contact the administrator."},
            })

        # Instantiate the form with the user's assigned laboratories
        form = LabSwitchForm(user_labs=user_labs)
        # Extract lab_id values from the user's groups
        lab_ids_list = list(user_labs.values_list('name', flat=True))

        # Filter Laboratories using those lab_ids
        lab_description = Laboratories.objects.filter(lab_id__in=lab_ids_list)
        return render(request, 'switch_lab.html', {
            'data': form,
            'lab_description' : lab_description
        })

    

# Functional view for displaying and updating user data and API tokens.
@login_required
def user_data_view(request):
    # Redirect to login if user is not authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    if request.method == 'POST':
        # Process submitted user data and API token forms
        form_user = UserDataForm(data=request.POST)
        form_api_tokens = APITokenForm(data=request.POST, username=user.username)

        # Save user data if valid
        if form_user.is_valid():
            user_data = form_user.save(commit=False)
            user_data.user_id = user.username
            user_data.save()

        # Save API tokens if valid and laboratory is selected
        if form_api_tokens.is_valid() and form_api_tokens.cleaned_data.get('laboratory'):
            lab = Laboratories.objects.get(pk=form_api_tokens.cleaned_data['laboratory'])
            api_token_queryset = API_Tokens.objects.filter(laboratory=lab, user_id=user.username)

            api_token = form_api_tokens.save(commit=False)
            # Update existing token if available
            if api_token_queryset.exists():
                existing_token = api_token_queryset.first()
                api_token.id = existing_token.id
                api_token.elab_token = api_token.elab_token or existing_token.elab_token
                api_token.jenkins_token = api_token.jenkins_token or existing_token.jenkins_token
                api_token.minio_acces_key = api_token.minio_acces_key or existing_token.minio_acces_key
                api_token.minio_secret_key = api_token.minio_secret_key or existing_token.minio_secret_key

            api_token.user_id = user.username
            api_token.save()

    # Load existing user data if available, otherwise create an empty form
    try:
        existing_user_data = Users.objects.get(pk=user.username)
        form_user = UserDataForm(instance=existing_user_data)
    except Users.DoesNotExist:
        form_user = UserDataForm()

    # Initialize API token form
    form_api_tokens = APITokenForm(username=user.username)

    # Render user data page with forms
    return render(request, 'home/utility_pages/user_data_page.html', {
        'user_data': form_user,
        'api_token_data': form_api_tokens,
    })

@login_required
@require_POST
def delete_sample_entry(request):
    sample_id = request.POST.get('sample_id')
    if sample_id:
        try:
            sample = Samples.objects.get(pk=sample_id)

            # Then delete subclass instance if it exists
            for subclass in Samples.__subclasses__():
                try:
                    subclass_instance = subclass.objects.get(samples_ptr=sample)
                    subclass_instance.delete()
                except subclass.DoesNotExist:
                    continue

            # Finally, delete the base sample
            sample.delete()
            messages.success(request, f"Sample {sample_id} deleted successfully.")
        except Samples.DoesNotExist:
            messages.error(request, f"Sample {sample_id} not found.")
        except Exception as e:
            messages.error(request, f"Error deleting sample: {e}")
    else:
        messages.error(request, "No sample ID provided.")

    return redirect(request.META.get('HTTP_REFERER', '/'))

# Delete ExperimentDMP and its intermediary relationships
from PRP_CDM_app.models.common_data_model import ExperimentDMP
from PRP_CDM_app.models.common_data_model import ExperimentDMPxSample, ExperimentDMPxInstrument, ExperimentDMPxLab

@login_required
@require_POST
def delete_experiment_dmp_entry(request):
    experiment_dmp_id = request.POST.get('experiment_dmp_id')
    if experiment_dmp_id:
        try:
            dmp = ExperimentDMP.objects.get(pk=experiment_dmp_id)
            # Delete the DMP
            dmp.delete()
            messages.success(request, f"Experiment DMP {experiment_dmp_id} deleted successfully.")
        except ExperimentDMP.DoesNotExist:
            messages.error(request, f"Experiment DMP {experiment_dmp_id} not found.")
        except Exception as e:
            messages.error(request, f"Error deleting Experiment DMP: {e}")
    else:
        messages.error(request, "No Experiment DMP ID provided.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_POST
def delete_result_entry(request):
    result_id = request.POST.get('result_id')
    if result_id:
        try:
            result = Results.objects.get(pk=result_id)

            # Delete the DMP
            result.delete()
            messages.success(request, f"Result {result_id} deleted successfully.")
        except ExperimentDMP.DoesNotExist:
            messages.error(request, f"Result {result_id} not found.")
        except Exception as e:
            messages.error(request, f"Error deleting Result: {e}")
    else:
        messages.error(request, "No Result ID provided.")

    return redirect(request.META.get('HTTP_REFERER', '/'))
