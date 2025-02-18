# Copyright (c) 2025 Marco Prenassi, Cecilia Zagni,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi, Cecilia Zagni
# Date: 2025-02-17
# Description: This file contains form classes used within the DECOS system, 
# and the form orchestrator to manage the dynamic sample forms from the laboratories contained in PRP_CDM_app.

# Decos Webapp - Home App
# Relative Path: home/forms.py

##
# Third-party imports
from django import forms
from django.contrib.auth.models import User, Group
from django.http import QueryDict


# Local application imports
from .secrets_models import API_Tokens
from PRP_CDM_app.fields import BooleanIfWhat, MultiChoicheAndOtherWidget

# This import points to the external app schema!
from PRP_CDM_app.forms import FormsDefinition
from PRP_CDM_app.models import (
    Users, 
    Proposals, 
    ServiceRequests, 
    Laboratories, 
    Samples,
    Instruments, 
    Results, 
    labDMP
)

# This form is used to switch between different user labs. It dynamically generates
# a ChoiceField based on the labs available to the user.
class LabSwitchForm(forms.Form):
    # Initialize the form with a list of user labs.
    def __init__(self, user_labs=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_labs = user_labs or []
        # Dynamically create a ChoiceField for selecting a lab.
        self.fields['lab_selected'] = forms.ChoiceField(choices=self._define_choices())

    # Generate choices for the ChoiceField based on user labs.
    def _define_choices(self):
        return [(lab.name, lab.name) for lab in self.user_labs]

# Form orchestrator to dynamically create forms based on user_lab
# Handles the exclusion of certain fields and custom widgets

def form_orchestrator(user_lab, request, filerequest, get_instance):
    if user_lab is None:
        return None
    try:
        form_class = getattr(FormsDefinition, user_lab.title() + "Form")
    except AttributeError:
        raise ValueError(f"Form definition for lab '{user_lab}' not found.")

    form_list = []
    for form_model in form_class.content:
        exclude, widgets_list = get_exclude_and_widgets(form_class, form_model)

        instance = form_model.objects.get(pk=request.GET['sample_id']) if get_instance else None

        form_list.append(
            form_factory(
                form_model, widgets_list, request=request, filerequest=filerequest,
                exclude_list=exclude, instance=instance
            )
        )
    return form_list

# Helper function to get exclusion list and widget configuration for a model

def get_exclude_and_widgets(form_class, form_model):
    exclude = form_class.exclude.get(form_model.__name__, []) if hasattr(form_class, 'exclude') else []
    widgets = getattr(form_model, 'widgets', {})
    return exclude, widgets

# Form factory to dynamically create ModelForm classes based on provided configurations
def form_factory(form_model, widgets_list=None, request=None, filerequest=None, exclude_list=None, instance=None):
    class CustomForm(forms.ModelForm):
        class Meta:
            model = form_model
            widgets = widgets_list or {}
            exclude = exclude_list or []

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    # Handle if request is data (e.g., QueryDict) or an actual request object
    if isinstance(request, dict) or isinstance(request, QueryDict):
        data = request
    elif request is not None:
        data = request.POST
    else:
        data = None

    return CustomForm(data=data, files=filerequest or None, instance=instance)
# DMP: for laboratory core data management plan form


class DMPform(forms.ModelForm):

        # see https://docs.djangoproject.com/en/1.9/topics/forms/ for more complex example.
        # We are using a ModelForm, it is not mandatory
        
        class Meta:
            model = labDMP
            # fields = ['datavarchar', 'dataint']
            widgets = {'instrument_metadata_collection': BooleanIfWhat(yes_or_no=True),
                       'additional_enotebook_open_collection': BooleanIfWhat(yes_or_no=True),
                       'sample_standard': BooleanIfWhat(yes_or_no=True),
                       'metadata_schema_defined': BooleanIfWhat(yes_or_no=True),
                       'open_data_licence':BooleanIfWhat(yes_or_no=True),
                       }
            exclude = ['lab_id', 'user_id']

# to manage the user data inside the decos_metadata_db ontology
class UserDataForm(forms.ModelForm):
    class Meta:
            model = Users
            # fields = ['datavarchar', 'dataint']
            '''widgets = {'gender': forms.SelectMultiple(),
                       'legal_status': forms.SelectMultiple(),
                       'research_role': forms.SelectMultiple(),
                       }'''
            exclude = ['user_id']

# this is a mockup/test form to insert instrument data before EPIRO
class InstrumentsForm(forms.ModelForm):

        # see https://docs.djangoproject.com/en/1.9/topics/forms/ for more complex example.
        # We are using a ModelForm, it is not mandatory
        
        class Meta:
            model = Instruments
            fields = ['vendor', 'model', 'description']

# to store the core elements of the results
class ResultsForm(forms.ModelForm):
        
        # see https://docs.djangoproject.com/en/1.9/topics/forms/ for more complex example.
        # We are using a ModelForm, it is not mandatory
        
        class Meta:
            model = Results
            fields = ['main_repository', 'article_doi']

# to add new laboratory in the admin panel
class AddNewLabForm(forms.ModelForm):
    class Meta:
            model = Laboratories
            fields = ['lab_id', 'description']

# to request and change api tokens in the user data page
class APITokenForm(forms.ModelForm):

    def __init__(self, username, *args, **kwargs):
        super(APITokenForm, self).__init__(*args, **kwargs)
        user = User.objects.filter(username=username).first()
        qset=Group.objects.filter(user = user, laboratory = True)
        lab_list = []
        for group in qset:
             lab_list.append(Laboratories.objects.get(lab_id=group.name).lab_id)
        qset = Laboratories.objects.filter(lab_id__in = lab_list)
        self.fields['laboratory'] = forms.ModelChoiceField(queryset=qset)
        

    class Meta:
        from .secrets_models import API_Tokens
        model = API_Tokens

        widgets = {
            'elab_token' : forms.PasswordInput(),
            'jenkins_token' : forms.PasswordInput(),
        }
        exclude = ['user_id']

### STUBS for DIMMT or proposal management, not entirely used right now--->
class ProposalSubmissionForm(forms.ModelForm):
    class Meta:
            model = Proposals
            # fields = ['datavarchar', 'dataint']
            exclude = ['proposal_id',
                       'user_id',
                       'proposal_status',
                       'proposal_feasibility',
                       #'proposal_submission_date'
                       ]
            
class SRSubmissionForm(forms.ModelForm):
    class Meta:
            model = ServiceRequests
            exclude = ['sr_id',
                       'sr_status',
                       'proposal_id',
                       ]
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SRSubmissionForm, self).__init__(*args, **kwargs)
        # if user is not None:
          #  self.fields['proposal_id'].queryset = Proposals.objects.filter(user_id=user)

class SRForSampleForm(forms.ModelForm):
    class Meta:
        model = Samples
        fields =  ['sr_id']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SRForSampleForm, self).__init__(*args, **kwargs)
        if user is not None:
            # Ottieni tutti i proposal_id associati all'utente loggato
            user_proposals = Proposals.objects.filter(user_id=user)
            # Filtra i sr_id basati su questi proposal_id
            self.fields['sr_id'].queryset = ServiceRequests.objects.filter(proposal_id__in=user_proposals)

class SRForSampleForm(forms.ModelForm):
    class Meta:
        model = Samples
        fields =  ['sr_id']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SRForSampleForm, self).__init__(*args, **kwargs)
        if user is not None:
            # Ottieni tutti i proposal_id associati all'utente loggato
            user_proposals = Proposals.objects.filter(user_id=user)
            # Filtra i sr_id basati su questi proposal_id
            self.fields['sr_id'].queryset = ServiceRequests.objects.filter(proposal_id__in=user_proposals)
# <----

