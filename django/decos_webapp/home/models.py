# Copyright (c) 2025 Marco Prenassi, Cecilia Zagni,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi, Cecilia Zagni
# Date: 2025-02-17
# Description: This models.py file is part of a Django Wagtail project that supports the development of 
# an experiment metadata catalog for life sciences laboratories, this page models are contained in the 
# decos_webapp_db, while the metadata catalog is referenced into PRP_CDM_App and decos_metadata_db.
# It defines custom Wagtail pages and data management components to handle samples, instruments, 
# research results, data management plans and related metadata. 
# The pages facilitate data entry, editing, and catalog visualization, enabling lab-specific 
# contextualization and linking of experimental data.
# NOTE: this page migrates to the default db.

# Decos Webapp - Home App
# Relative Path: 


##
# Standard Library Imports
import json  # For handling JSON data
import logging  # For logging errors, warnings, and info
from os import listdir  # For listing files in a directory
from os.path import dirname, isfile, join  # For file path manipulations
from django.http import HttpResponseRedirect # Required for checking redirect responses when validating lab session

# Third-party Imports (Django & Wagtail)
from django import forms  # For form handling
from django.conf import settings  # For accessing Django settings
from django.contrib.auth.models import Group, User  # User and Group models
from django.core.exceptions import ObjectDoesNotExist  # For handling non-existing objects
from django.db import connections, models  # ORM models and DB connections
from django.forms.models import model_to_dict  # For converting model instances to dictionaries
from django.shortcuts import redirect, render, get_object_or_404  # For rendering templates and handling redirects
from django.template.loader import render_to_string  # For rendering templates to strings
from django_tables2.config import RequestConfig  # For configuring table display
from django.apps import apps

from wagtail.admin.panels import (  # For Wagtail admin panel configurations 
    FieldPanel, 
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import (  # For Wagtail settings models
    BaseGenericSetting, 
    register_setting
)
from wagtail.fields import RichTextField  # For rich text fields in Wagtail models
from wagtail.models import Page  # Base Page model in Wagtail CMS

# Local Application Imports (Project-specific)

from .decos_elab import DecosElabAPI  # Integration with Decos Elab API
from .decos_jenkins import DecosJenkinsAPI  # Integration with Decos Jenkins API

from .forms import (  # Project-specific forms
    APITokenForm,
    DMPform,
    ExperimentDMPForm,
    InstrumentsForm,
    LabSwitchForm,
    ResultsForm,
    SRSubmissionForm,
    UserDataForm,
    ProposalSubmissionForm,
    form_orchestrator,  # Orchestrates form handling
)

from .secrets_models import API_Tokens  # Model for API tokens

from .tables import (  # Django-tables2 configurations for displaying data tables
    InstrumentsSelectionTable,
    ProposalsTable,
    ResultsTable,
    SamplesSelectionTable,
    SamplesTable,
    ServiceRequestTable,
    ExperimentDMPTable
)

from PRP_CDM_app.code_generation import (  # ID code generators for various entities
    experimentdmp_id_generation,
    instrument_id_generation,
    proposal_id_generation,
    result_id_generation,
    sample_id_generation,
    sr_id_generation,
    xid_code_generation,
)

from PRP_CDM_app.models.common_data_model import (  # Models related to samples, instruments, results, etc.
    ExperimentDMP,
    ExperimentDMPxInstrument,
    ExperimentDMPxLab,
    ExperimentDMPxSample,
    LabXInstrument,
    Laboratories,
    Proposals,
    ResultxInstrument,
    ResultxSample,
    Results,
    Samples,
    ServiceRequests,
    Users,
    Instruments,
    labDMP,
)

from PRP_CDM_app.models.laboratory_models.lage import LageSamples

from APIs.decos_minio_API.decos_minio_API import decos_minio  # MinIO API integration

try:
    Group.add_to_class('laboratory', models.BooleanField(default=False))
except:
    print("meh") # FIXME: CATCH THIS IT IS

logger = logging.getLogger(__name__)

# HeaderSettings allows customization of the website's header section, enabling
# administrators to set a custom text and upload an icon via the Wagtail admin interface.
@register_setting
class HeaderSettings(BaseGenericSetting):
    header_text = RichTextField(blank=True, verbose_name="Header Text", help_text="Text displayed in the website header")
    prp_icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Header Icon",
        help_text="Icon displayed in the header"
    )

# FooterSettings provides customization options for the website's footer section,
# allowing administrators to configure footer text with room for future enhancements.
@register_setting
class FooterSettings(BaseGenericSetting):
    footer_text = models.TextField(blank=True, verbose_name="Footer Text", help_text="Text displayed in the website footer")
    # TODO: Add fields for copyright notice and social media links in the future

# ApiSettings creates a configuration menu in the admin panel to specify API URLs
# for external services (eLab, Jenkins), with potential future support for MinIO integration.
@register_setting
class ApiSettings(BaseGenericSetting):
    elab_base_url = models.URLField(
        verbose_name="eLab Base URL",
        blank=True,
        help_text="Base URL for the eLab API"
    )
    jenkins_base_url = models.URLField(
        verbose_name="Jenkins Base URL",
        blank=True,
        help_text="Base URL for the Jenkins API"
    )
    minio_base_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="MinIo Endpoint",
        help_text="Minio endpoint"
    )

# template: file://./templates/home/home_page.html
# HomePage is a customizable home page model for Wagtail CMS.
# It allows content editors to set an introductory text and rich body content.
class HomePage(Page):
    # A short introductory text displayed on the home page.
    intro = models.CharField(
        max_length=250,
        default="",
        help_text="Short introductory text displayed on the home page."
    )

    # Main body content of the home page, supports rich text formatting.
    body = RichTextField(
        blank=True,
        help_text="Main body content of the home page, supports rich text formatting."
    )

    # Defines the fields displayed in the Wagtail admin interface.
    content_panels = [
        FieldPanel("title"),  # Built-in title field from Wagtail Page model
        FieldPanel("intro"),  # Introductory text panel
        FieldPanel("body"),   # Rich text content panel
    ]

# Retrieves the selected laboratory from session data
class SessionHandlerMixin:
    def get_lab_from_session(self, request):
        lab_id = request.session.get('lab_selected')
        if not lab_id:
            return None

        try:
            return Laboratories.objects.get(pk=lab_id)
        except Laboratories.DoesNotExist:
            return None

# Provides common utilities for handling sample data, service request linking, and selecting laboratory-specific form templates.
class SampleFormHandlerMixin:
    # Retrieves the Sample object and its associated laboratory based on the provided sample ID
    def get_sample_and_lab(self, sample_id):
        sample = Samples.objects.get(pk=sample_id)
        return sample, sample.lab_id
    
    # Assigns a ServiceRequest object to the data if a valid service request ID is provided
    def assign_service_request(self, data, sr_id):
        if sr_id and sr_id != 'internal':
            data.sr_id = ServiceRequests.objects.get(pk=sr_id)

    # Validates and saves data from multiple forms, linking to sample, lab, and optionally generating sample ID
    def process_forms(self, forms, sample=None, lab=None, request=None, generate_sample_id=False):
        saved_objects = []
        for form in forms:
            if not form.is_valid():
                return False, form.errors

            data = form.save(commit=False)

            if request:
                self.assign_service_request(data, request.POST.get("sr_id_hidden"))

            if sample:
                data.sample_id = sample.sample_id
                data.sample_location = sample.sample_location
            elif generate_sample_id:
                data.sample_id = sample_id_generation(data.sr_id)

            data.lab_id = lab
            data.sample_status = 'Submitted'
            data.save()
            saved_objects.append(data)

        return True, saved_objects

    # Determines the appropriate form template for a given laboratory, falling back to a generic template if not found
    def get_form_template(self, lab_id):
        try:
            abs_path = join(settings.BASE_DIR, 'home/templates/home/forms/')
            formlist = [f for f in listdir(abs_path)]
        except Exception as e:
            return 'home/forms/generic_form_page.html'

        for template in formlist:
            if lab_id.lower() in template.lower():
                return f'home/forms/{template}'

        return 'home/forms/generic_form_page.html'

# Manages the lifecycle of updating existing sample data, integrating dynamic form initialization and submission validation.
class EditSamplePage(Page, SampleFormHandlerMixin):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]
    # Handles the HTTP request lifecycle for editing an existing sample's data
    def serve(self, request):
        if request.method == 'POST':
            sample, lab = self.get_sample_and_lab(request.POST['sample_id_hidden'])
            forms = form_orchestrator(user_lab=lab.lab_id, request=request.POST, filerequest=request.FILES, get_instance=False)
            success, result = self.process_forms(forms, sample=sample, lab=lab, request=request)
            if success:
                return render(request, 'home/thank_you_page.html', {'page': self, 'data': result})
            
            # Reinitialize forms with existing sample data upon validation failure
            forms = form_orchestrator(user_lab=lab.lab_id, request=request, filerequest=None, get_instance=True)
            context = {'page': self, 'lab': lab.lab_id, 'sr_id': sample.sr_id, 'sample_id': sample.sample_id, 'forms': forms, 'errors': result}
            for form in forms:
                context[form.Meta.model.__name__] = form

            template = self.get_form_template(lab.lab_id)
            return render(request, template, context)

        sample, lab = self.get_sample_and_lab(request.GET['sample_id'])
        forms = form_orchestrator(user_lab=lab.lab_id, request=request, filerequest=None, get_instance=True)

        context = {'page': self, 'lab': lab.lab_id, 'sr_id': sample.sr_id, 'sample_id': sample.sample_id, 'forms': forms}
        for form in forms:
            context[form.Meta.model.__name__] = form

        template = self.get_form_template(lab.lab_id)
        return render(request, template, context)

# Add new samples, supporting service request linking and laboratory-specific forms within a session-based workflow.
class SamplePage(Page, SessionHandlerMixin, SampleFormHandlerMixin):
    intro = RichTextField(blank=True)
    thankyou_page_title = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('thankyou_page_title'),
    ]
    
    # Handles the HTTP request lifecycle for creating a new sample
    def serve(self, request):
        lab = self.get_lab_from_session(request)
        if not lab:
            request.session['return_page'] = request.get_full_path()
            return redirect('/switch-laboratory')

        sr_id = request.GET.get("sr_id", "internal")
        filter_term = request.GET.get("filter", "")

        if request.method == 'POST':
            forms = form_orchestrator(user_lab=lab.lab_id, request=request.POST, filerequest=request.FILES, get_instance=False)
            success, result = self.process_forms(forms, lab=lab, request=request, generate_sample_id=True)

            if success:
                return render(request, 'home/thank_you_page.html', {'page': self, 'data': result})
            
            # Retains selected service request ID and displays errors upon validation failure
            sr_id = request.POST.get("sr_id_hidden", "internal")
            context = {'page': self, 'forms': forms, 'lab': lab.lab_id, 'sr_id': sr_id, 'table': None, 'errors': result}
        else:
            forms = form_orchestrator(user_lab=lab.lab_id, request=None, filerequest=None, get_instance=False)
            sr_query = ServiceRequests.objects.filter(lab_id=lab.lab_id)
            if filter_term:
                sr_query = sr_query.filter(sr_id__icontains=filter_term)

            sr_table = ServiceRequestTable(sr_query)
            RequestConfig(request).configure(sr_table)

            context = {'page': self, 'forms': forms, 'lab': lab.lab_id, 'sr_id': sr_id, 'table': sr_table}

        for form in forms:
            context[form.Meta.model.__name__] = form

        template = self.get_form_template(lab.lab_id)
        return render(request, template, context)

# Displays and manages a paginated list of samples for a selected laboratory,
# integrating eLab submissions and MinIO for data synchronization.
class SampleListPage(Page, SessionHandlerMixin):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    def _get_lab_or_redirect(self, request):
        # Retrieves lab from session or redirects to lab selection.
        lab = self.get_lab_from_session(request)
        if not lab:
            request.session['return_page'] = request.get_full_path()
            return None, redirect('/switch-laboratory')
        return lab, None

    def _handle_elab_submission(self, request, lab, username):
        # Submits sample data to the external eLab system.
        sample_id = request.POST.get('elab_write')
        if not sample_id:
            return

        try:
            token = API_Tokens.objects.filter(laboratory=lab.lab_id, user_id=User.objects.get(username=username)).first()
            elab_api = DecosElabAPI(ApiSettings.objects.get(pk=1).elab_base_url, token.elab_token)
            sample = Samples.objects.get(pk=sample_id)
            elab_api.create_new_decos_experiment(lab=lab, username=username, experiment_info=sample)
        except (ObjectDoesNotExist, UnboundLocalError) as e:
            logger.error(f"Elab submission failed: {e}")

    def _refresh_minio_samples(self, request, lab, username):
        # Updates sample locations from MinIO storage if requested.
        if request.POST.get('refresh') != 'true':
            return ""

        try:
            tokens = API_Tokens.objects.filter(laboratory=lab.lab_id, user_id=User.objects.get(username=username)).first()
            client = decos_minio(endpoint=ApiSettings.objects.all().first().minio_base_url, access_key=tokens.minio_acces_key, secret_key=tokens.minio_secret_key)
            data_locations = client.get_sample_list(lab=lab)
        except Exception as e:
            logger.error(f"MinIO data refresh failed: {e}")
            return f"Error on MinIO: {e}"

        samples = Samples.objects.filter(lab_id=lab.lab_id)
        for sample in samples:
            location = next((loc.object_name for sample_id, loc in data_locations if sample.pk == sample_id), None)
            sample.sample_location = location
            sample.save()

        return "minIO buckets read correctly"

    def serve(self, request):
        # Handles sample list display and optional form actions (filtering, eLab submission, MinIO refresh).
        lab, redirect_response = self._get_lab_or_redirect(request)
        if redirect_response:
            return redirect_response

        filter_term = request.POST.get('filter') or request.GET.get('filter', '')
        minIO_status = ""

        if request.method == 'POST':
            username = request.user.username if request.user.is_authenticated else ""
            self._handle_elab_submission(request, lab, username)
            minIO_status = self._refresh_minio_samples(request, lab, username)

        samples = Samples.objects.filter(lab_id=lab.lab_id, sample_id__icontains=filter_term)
        table = SamplesTable(samples)
        RequestConfig(request).configure(table)
        table.paginate(page=request.GET.get('page', 1), per_page=5)

        return render(request, 'home/sample_pages/sample_list.html', {
            'page': self,
            'table': table,
            'minio_filelist_status': minIO_status,
        })

# Display and trigger post-processing pipelines via Jenkins - STUB
class PipelinesPage(Page): # EASYDMP
    # Intro text field for the page
    intro = RichTextField(blank=True)
    # Define the content panels displayed in the admin interface
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    def serve(self, request):
        # Pipeline identifier hardcoded for now
        pipeline_name = "test_pipeline_with_parameters"
        # Secret token required to trigger the pipeline
        secret_token = "parameter_test_pipeline_SECRET_TOKEN"

        # Check if the user is authenticated before proceeding
        if request.user.is_authenticated:
            # Get the logged-in user's username
            username = request.user.username
            # Retrieve the selected lab from the user's session
            lab = request.session.get('lab_selected')
            # Initialize the Jenkins API handler with user context
            jenkins_api = DecosJenkinsAPI(username=username, lab=lab)

            # Handle POST request to trigger the pipeline
            if request.method == 'POST':
                # Retrieve sample ID from the form submission
                sample_id = request.POST.get("pipelines", None)
                # Prepare data payload including sample ID (used in pipeline execution)
                data = {"data0": sample_id, "data1": "DATA001"}

                # Start the pipeline if a sample ID was provided
                if sample_id:
                    jenkins_api.start_pipeline(pipeline_name=pipeline_name, secret_token=secret_token, data=data)

            # Fetch console output from Jenkins for the pipeline execution
            output = jenkins_api.get_pipeline_output(pipeline_name=pipeline_name)

            # Check if output is requested via GET parameter
            if request.GET.get("output", None):
                # Render the page with console output and sample ID
                return render(request, 'home/sample_pages/pipelines_page.html', {
                    'page': self,
                    'sample_id': request.GET.get("pipelines", None),
                    'console_output': output
                })

        # Render the page without console output (initial state or non-authenticated users)
        return render(request, 'home/sample_pages/pipelines_page.html', {
            'page': self,
            'sample_id': request.GET.get("pipelines", None),
        })

# Model handling of the core Data Management Plan (DMP) submissions for life science laboratories, ensuring lab context via session and supporting form-based data entry.
class DMPPage(Page, SessionHandlerMixin):
    # Wagtail Page model for managing Data Management Plans (DMP) per laboratory
    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
        max_length=255, help_text="Title text displayed after DMP submission")

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('thankyou_page_title'),
    ]

    def serve(self, request):
        # Ensure a laboratory context is set in the session
        if not self.is_lab_selected(request):
            return self.redirect_to_lab_selection(request)

        # Route request to the appropriate handler based on HTTP method
        if request.method == 'POST':
            return self.handle_post(request)
        return self.handle_get(request)

    def is_lab_selected(self, request):
        # Check if the session contains a valid laboratory context
        return 'lab_selected' in request.session and request.session['lab_selected'] is not None

    def redirect_to_lab_selection(self, request):
        # Store the current page as return point, then redirect to lab selection page
        request.session['return_page'] = request.META.get('HTTP_REFERER', '/')
        return redirect(request.POST.get('next', '/switch-laboratory'))

    def handle_post(self, request):
        # Handle DMP submission; validate and save form data
        form = DMPform(data=request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.lab_id = request.session['lab_selected']
            data.user_id = request.user.username
            data.save()

            return render(request, 'home/dmp_pages/labdmp_page.html', {
                'page': self,
                'data': form,
                'lab': self.get_lab_from_session(request),
            })

        # Render error page if form validation fails
        return render(request, 'home/error_page.html', {
            'page': self,
            'form': form,  # Pass form object to display field-specific errors
        })

    def handle_get(self, request):
        # Retrieve existing DMP for selected lab or initialize empty form
        lab_selected = request.session['lab_selected']
        try:
            lab_instance = labDMP.objects.get(pk=lab_selected)
            form = DMPform(instance=lab_instance)
        except labDMP.DoesNotExist:
            form = DMPform()

        return render(request, 'home/dmp_pages/labdmp_page.html', {
            'page': self,
            'data': form,
            'lab': lab_selected,
        })

# Test page to insert instruments
class InstrumentsPage(Page): # EASYDMP STUB! EPIRO WILL TAKE THIS FUNCTIONALITY
    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
        max_length=255, help_text="Title text to use for the 'thank you' page")
    # Note that there's nothing here for specifying the actual form fields -
    # those are still defined in forms.py. There's no benefit to making these
    # editable within the Wagtail admin, since you'd need to make changes to
    # the code to make them work anyway.

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('thankyou_page_title'),
    ]

    def serve(self,request):
        if request.user.is_authenticated:
            username = request.user.username
        
        try:
            if(request.session['lab_selected'] is None):
                request.session["return_page"] = request.META['HTTP_REFERER']
                next = request.POST.get("next", "/switch-laboratory")
                return redirect(next)
        except KeyError:
            request.session["return_page"] = request.META['HTTP_REFERER']
            next = request.POST.get("next", "/switch-laboratory")
            return redirect(next)
        
        lab = request.session['lab_selected']

        if request.method == 'POST':
            # If the method is POST, validate the data and perform a save() == INSERT VALUE INTO
            form = InstrumentsForm(data=request.POST)
            if form.is_valid():
                # BEWARE: This is a modelForm and not a object/model, "save" do not have some arguments of the same method, like using=db_tag
                # to work with a normal django object insert a line: data = form.save(commit=False) and then data is a basic model: e.g., you can use data.save(using=external_generic_db)
                # In our example the routing takes care of the external db save
                data = form.save(commit=False)
                data.instrument_id = instrument_id_generation(form['vendor'].data, form['model'].data)
                data.save()
                labxinstrument = LabXInstrument()
                labxinstrument.lab_id = Laboratories.objects.get(pk = lab)
                labxinstrument.instrument_id = data
                labxinstrument.save()
                # data.lab_id = request.session["lab_selected"]
                # data.user_id = username
                # data.save()
                return render(request, 'home/lab_management_pages/instruments_page.html', { # TODO: softcode the template selection
                    'page': self,
                    # We pass the data to the thank you page, data.datavarchar and data.dataint!
                    'data': form,
                    'lab': request.session['lab_selected'],
                })
            else:
                return render(request, 'home/error_page.html', {
                        'page': self,
                        # We pass the data to the thank you page, data.datavarchar and data.dataint!
                        'errors': form.errors, # TODO: improve this
                    })
        form = InstrumentsForm()
        return render(request, 'home/lab_management_pages/instruments_page.html', {
                'page': self,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'data': form,
                'lab': request.session['lab_selected'],
            })

# This page adds research result information to create the metadata catalog, linking samples, instruments, and core data management plan.
class ResultsPage(Page, SessionHandlerMixin):
    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
        max_length=255, help_text="Title text to use for the 'thank you' page")

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('thankyou_page_title'),
    ]

    # Utility method to extract list values from GET parameters
    def get_list_from_request(self, request, list_key, id_key):
        items = []
        if list_key in request.GET:
            items = json.loads(request.GET.get(list_key, '[]'))
        if id_key in request.GET:
            item_id = request.GET.get(id_key)
            if item_id:
                items.append(item_id)
        return items

    # Utility method to determine if a filter dropdown should be open
    def is_filter_open(self, request, filter_key):
        return "open " if request.GET.get(filter_key, "") else " "

    # Checks for lab session or redirects to lab switch page
    def get_lab_from_session_or_redirect(self, request):
        try:
            if self.get_lab_from_session(request) is None:
                request.session["return_page"] = request.META.get('HTTP_REFERER', '/')
                return redirect("/switch-laboratory")
        except KeyError:
            request.session["return_page"] = request.META.get('HTTP_REFERER', '/')
            return redirect("/switch-laboratory")
        return request.session['lab_selected']

    # Handles POST form submission for creating Results and linking related objects
    def handle_form_submission(self, request, sample_list, instrument_list, software_list):
        form = ResultsForm(data=request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            result_id = result_id_generation(data)
            data.result_id = result_id
            data.save()

            result = data

            # Bulk-fetch samples to reduce database hits
            samples = Samples.objects.filter(sample_id__in=sample_list)
            for sample in samples:
                ResultxSample.objects.get_or_create(
                    x_id=xid_code_generation(result_id, sample.sample_id),
                    results=result, samples=sample
                )

            # Bulk-fetch instruments to reduce database hits
            instruments = Instruments.objects.filter(instrument_id__in=instrument_list)
            for instrument in instruments:
                ResultxInstrument.objects.get_or_create(
                    x_id=xid_code_generation(result_id, instrument.instrument_id),
                    results=result, instruments=instrument
                )

            return render(request, 'home/thank_you_page.html', {'page': self, 'data': data})
        else:
            return render(request, 'home/error_page.html', {'page': self, 'errors': form.errors})

    def serve(self, request):
        # Validate lab session or redirect
        lab = self.get_lab_from_session_or_redirect(request)
        if isinstance(lab, HttpResponseRedirect):
            return lab

        # Extract lists for samples, datasets, instruments, and software
        sample_list = self.get_list_from_request(request, 'sample_list', 'sample_id')
        public_dataset_list = self.get_list_from_request(request, 'public_dataset_list', 'public_dataset_location')
        instrument_list = self.get_list_from_request(request, 'instrument_list', 'instrument_id')
        software_list = self.get_list_from_request(request, 'software_list', 'software_id')

        # Handle form submission
        if request.method == 'POST':
            return self.handle_form_submission(request, sample_list, instrument_list, software_list)

        # Open/close dropdown filter indicators
        sample_filter_set = self.is_filter_open(request, "sample_filter")
        instrument_filter_set = self.is_filter_open(request, "instrument_filter")

        # Filters and additional GET params
        sample_filter = request.GET.get("sample_filter", "")
        instrument_filter = request.GET.get("instrument_filter", "")
        article_doi = request.GET.get("article_doi", "")
        main_repository = request.GET.get("main_repository", "")

        # Query samples for the table display
        sample_query = Samples.objects.filter(lab_id=lab)
        if sample_filter:
            sample_query = sample_query.filter(sample_id__contains=sample_filter)
        sample_table = SamplesSelectionTable(sample_query, prefix="sample_")
        RequestConfig(request).configure(sample_table)
        sample_table.paginate(page=request.GET.get("sample_page", 1), per_page=5)

        # Query instruments for the table display
        instrument_query = Instruments.objects.all()
        if instrument_filter:
            instrument_query = instrument_query.filter(instrument_id__contains=instrument_filter)
        instrument_table = InstrumentsSelectionTable(instrument_query, prefix="inst_")
        RequestConfig(request).configure(instrument_table)
        instrument_table.paginate(page=request.GET.get("inst_page", 1), per_page=5)

        # Prepare data for template
        return render(request, 'home/lab_management_pages/results_page.html', {
            'page': self,
            'lab': lab,
            'article_doi': article_doi,
            'main_repository': main_repository,
            'sample_table': sample_table,
            'sample_filter': sample_filter_set,
            'instrument_filter': instrument_filter_set,
            'sample_list': json.dumps(sample_list),
            'sample_list_view': sample_list,
            'public_dataset_list': json.dumps(public_dataset_list),
            'public_dataset_list_view': public_dataset_list,
            'instruments_table': instrument_table,
            'instrument_list': json.dumps(instrument_list),
            'instrument_list_view': instrument_list,
            'software_list': json.dumps(software_list),
            'software_list_view': software_list,
        })

# This page displays a list of research results, filtered by lab and result ID, with pagination support.
class ResultsListPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    # Retrieves lab from session; redirects if not set or invalid
    def get_lab_from_session_or_redirect(self, request):
        lab_id = request.session.get('lab_selected')
        if not lab_id:
            request.session["return_page"] = request.META.get('HTTP_REFERER', '/')
            return redirect("/switch-laboratory")
        try:
            return Laboratories.objects.get(pk=lab_id)
        except Laboratories.DoesNotExist:
            return redirect("/switch-laboratory")

    def serve(self, request):
        lab = self.get_lab_from_session_or_redirect(request)
        if isinstance(lab, HttpResponseRedirect):
            return lab

        filter_value = request.GET.get('filter', '') or request.POST.get('filter', '')

        # TODO: manage lab view only or something else
        data = Results.objects.all()

        if filter_value:
            # Filters results by partial match on result_id
            data = data.filter(result_id__icontains=filter_value)

        # Configures results table with pagination
        table = ResultsTable(data)
        RequestConfig(request).configure(table)
        table.paginate(page=request.GET.get("page", 1), per_page=5)

        return render(request, 'home/lab_management_pages/results_list_page.html', {
            'page': self,
            'table': table,
            'filter_value': filter_value,
        })

# This page displays detailed information about a selected research result, including associated samples, instruments, and the lab's data management plan (DMP).
class ExperimentMetadataReportPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    # Retrieves lab from session; redirects if not set or invalid
    def get_lab_from_session_or_redirect(self, request):
        lab_id = request.session.get('lab_selected')
        if not lab_id:
            request.session["return_page"] = request.META.get('HTTP_REFERER', '/')
            return redirect("/switch-laboratory")
        return get_object_or_404(Laboratories, pk=lab_id)

    def serve(self, request):
        lab = self.get_lab_from_session_or_redirect(request)
        if isinstance(lab, HttpResponseRedirect):
            return lab

        result_id = request.GET.get("result_id")
        data = get_object_or_404(Results, pk=result_id)

        # Retrieve sample IDs related to the result
        sample_ids = ResultxSample.objects.filter(results=data).values_list('samples_id', flat=True)

        # Fetch all samples including their possible specializations
        samples = Samples.objects.filter(pk__in=sample_ids).select_related('lab_id')

        # Dynamically determine and replace specialized sample models
        specialized_samples = []
        for sample in samples:
            lab_name = sample.lab_id.lab_id.capitalize() # LAGE -> Lage or sissa -> Sissa
            specialized_sample_model_name = f"{lab_name}Samples" # Lage -> LageSamples ...
            SpecializedSamplesModel = apps.get_model('PRP_CDM_app', specialized_sample_model_name) if apps.is_installed('PRP_CDM_app') else None

            if SpecializedSamplesModel:
                specialized_sample = SpecializedSamplesModel.objects.filter(pk=sample.pk).first()
                if specialized_sample:
                    specialized_samples.append(specialized_sample)
                else:
                    specialized_samples.append(sample)
            else:
                specialized_samples.append(sample)

        # Retrieve instruments efficiently
        instrument_ids = ResultxInstrument.objects.filter(results=data).values_list('instruments_id', flat=True)
        instrument_list = list(Instruments.objects.filter(pk__in=instrument_ids))

        # Get lab DMP (handling missing case properly)
        lab_dmp = labDMP.objects.filter(pk=lab.lab_id).first()

        return render(request, 'home/lab_management_pages/experiment_metadata_report_page.html', {
            'page': self,
            'data': data,
            'sample_list': specialized_samples if specialized_samples else None,
            'instrument_list': instrument_list if instrument_list else None,
            'lab_dmp': lab_dmp if lab_dmp else None,
        })

class ExperimentDMPPage(Page, SessionHandlerMixin):
    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
        max_length=255, help_text="Title text to use for the 'thank you' page")

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('thankyou_page_title'),
    ]

    # Utility method to extract list values from GET parameters
    def get_list_from_request(self, request, list_key, id_key):
        items = []
        if list_key in request.GET:
            items = json.loads(request.GET.get(list_key, '[]'))
        if id_key in request.GET:
            item_id = request.GET.get(id_key)
            if item_id:
                items.append(item_id)
        return items

    # Utility method to determine if a filter dropdown should be open
    def is_filter_open(self, request, filter_key):
        return "open " if request.GET.get(filter_key, "") else " "

    # Checks for lab session or redirects to lab switch page
    def get_lab_from_session_or_redirect(self, request):
        try:
            if self.get_lab_from_session(request) is None:
                request.session["return_page"] = request.META.get('HTTP_REFERER', '/')
                return redirect("/switch-laboratory")
        except KeyError:
            request.session["return_page"] = request.META.get('HTTP_REFERER', '/')
            return redirect("/switch-laboratory")
        return request.session['lab_selected']

    # Handles POST form submission for creating Results and linking related objects
    def handle_form_submission(self, request, sample_list, instrument_list, software_list):
        form = ExperimentDMPForm(data=request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            experiment_dmp_id = result_id_generation(data)
            data.experiment_dmp_id = experimentdmp_id_generation(data)
            data.save()

            experiment_dmp = data

            # Bulk-fetch samples to reduce database hits
            samples = Samples.objects.filter(sample_id__in=sample_list)
            for sample in samples:
                ExperimentDMPxSample.objects.get_or_create(
                    x_id=xid_code_generation(experiment_dmp_id, sample.sample_id),
                    experiment_dmp=experiment_dmp, samples=sample
                )

            # Bulk-fetch instruments to reduce database hits
            instruments = Instruments.objects.filter(instrument_id__in=instrument_list)
            for instrument in instruments:
                ExperimentDMPxInstrument.objects.get_or_create(
                    x_id=xid_code_generation(experiment_dmp_id, instrument.instrument_id),
                    experiment_dmp=experiment_dmp, instruments=instrument
                )

            return render(request, 'home/thank_you_page.html', {'page': self, 'data': data})
        else:
            return render(request, 'home/error_page.html', {'page': self, 'errors': form.errors})

    def serve(self, request):
        # Validate lab session or redirect
        lab = self.get_lab_from_session_or_redirect(request)
        if isinstance(lab, HttpResponseRedirect):
            return lab

        # Extract lists for samples, datasets, instruments, and software
        sample_list = self.get_list_from_request(request, 'sample_list', 'sample_id')
        public_dataset_list = self.get_list_from_request(request, 'public_dataset_list', 'public_dataset_location')
        instrument_list = self.get_list_from_request(request, 'instrument_list', 'instrument_id')
        software_list = self.get_list_from_request(request, 'software_list', 'software_id')

        # Handle form submission
        if request.method == 'POST':
            return self.handle_form_submission(request, sample_list, instrument_list, software_list)

        # Open/close dropdown filter indicators
        sample_filter_set = self.is_filter_open(request, "sample_filter")
        instrument_filter_set = self.is_filter_open(request, "instrument_filter")

        # Filters and additional GET params
        sample_filter = request.GET.get("sample_filter", "")
        instrument_filter = request.GET.get("instrument_filter", "")
        article_doi = request.GET.get("article_doi", "")
        main_repository = request.GET.get("main_repository", "")

        # Query samples for the table display
        sample_query = Samples.objects.filter(lab_id=lab)
        if sample_filter:
            sample_query = sample_query.filter(sample_id__contains=sample_filter)
        sample_table = SamplesSelectionTable(sample_query, prefix="sample_")
        RequestConfig(request).configure(sample_table)
        sample_table.paginate(page=request.GET.get("sample_page", 1), per_page=5)

        # Query instruments for the table display
        instrument_query = Instruments.objects.all()
        if instrument_filter:
            instrument_query = instrument_query.filter(instrument_id__contains=instrument_filter)
        instrument_table = InstrumentsSelectionTable(instrument_query, prefix="inst_")
        RequestConfig(request).configure(instrument_table)
        instrument_table.paginate(page=request.GET.get("inst_page", 1), per_page=5)

        # Prepare data for template
        return render(request, 'home/lab_management_pages/experiment_dmp_page.html', {
            'page': self,
            'lab': lab,
            'article_doi': article_doi,
            'main_repository': main_repository,
            'sample_table': sample_table,
            'sample_filter': sample_filter_set,
            'instrument_filter': instrument_filter_set,
            'sample_list': json.dumps(sample_list),
            'sample_list_view': sample_list,
            'public_dataset_list': json.dumps(public_dataset_list),
            'public_dataset_list_view': public_dataset_list,
            'instruments_table': instrument_table,
            'instrument_list': json.dumps(instrument_list),
            'instrument_list_view': instrument_list,
            'software_list': json.dumps(software_list),
            'software_list_view': software_list,
        })

class ExperimentDMPListPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    # Retrieves lab from session; redirects if not set or invalid
    def get_lab_from_session_or_redirect(self, request):
        lab_id = request.session.get('lab_selected')
        if not lab_id:
            request.session["return_page"] = request.META.get('HTTP_REFERER', '/')
            return redirect("/switch-laboratory")
        try:
            return Laboratories.objects.get(pk=lab_id)
        except Laboratories.DoesNotExist:
            return redirect("/switch-laboratory")

    def serve(self, request):
        lab = self.get_lab_from_session_or_redirect(request)
        if isinstance(lab, HttpResponseRedirect):
            return lab

        filter_value = request.GET.get('filter', '') or request.POST.get('filter', '')

        # TODO: manage lab view only or something else
        data = ExperimentDMP.objects.all()

        if filter_value:
            # Filters results by partial match on result_id
            data = data.filter(experiment_dmp_id__icontains=filter_value)

        # Configures results table with pagination
        table = ExperimentDMPTable(data)
        RequestConfig(request).configure(table)
        table.paginate(page=request.GET.get("page", 1), per_page=5)

        return render(request, 'home/lab_management_pages/experiment_dmp_list_page.html', {
            'page': self,
            'table': table,
            'filter_value': filter_value,
        })

class ExperimentDMPReportPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    # Retrieves lab from session; redirects if not set or invalid
    def get_lab_from_session_or_redirect(self, request):
        lab_id = request.session.get('lab_selected')
        if not lab_id:
            request.session["return_page"] = request.META.get('HTTP_REFERER', '/')
            return redirect("/switch-laboratory")
        return get_object_or_404(Laboratories, pk=lab_id)

    def serve(self, request):
        lab = self.get_lab_from_session_or_redirect(request)
        if isinstance(lab, HttpResponseRedirect):
            return lab

        experiment_dmp_id = request.GET.get("experiment_dmp_id")
        data = get_object_or_404(ExperimentDMP, pk=experiment_dmp_id)

        # Retrieve sample IDs related to the result
        sample_ids = ExperimentDMPxSample.objects.filter(experiment_dmp=data).values_list('samples_id', flat=True)

        # Fetch all samples including their possible specializations
        samples = Samples.objects.filter(pk__in=sample_ids).select_related('lab_id')

        # Dynamically determine and replace specialized sample models
        specialized_samples = []
        for sample in samples:
            lab_name = sample.lab_id.lab_id.capitalize() # LAGE -> Lage or sissa -> Sissa
            specialized_sample_model_name = f"{lab_name}Samples" # Lage -> LageSamples ...
            SpecializedSamplesModel = apps.get_model('PRP_CDM_app', specialized_sample_model_name) if apps.is_installed('PRP_CDM_app') else None

            if SpecializedSamplesModel:
                specialized_sample = SpecializedSamplesModel.objects.filter(pk=sample.pk).first()
                if specialized_sample:
                    specialized_samples.append(specialized_sample)
                else:
                    specialized_samples.append(sample)
            else:
                specialized_samples.append(sample)

        # Retrieve instruments
        instrument_ids = ExperimentDMPxInstrument.objects.filter(experiment_dmp=data).values_list('instruments_id', flat=True)
        instrument_list = list(Instruments.objects.filter(pk__in=instrument_ids))

        # Get lab DMP (handling missing case properly)
        lab_dmp = labDMP.objects.filter(pk=lab.lab_id).first()

        return render(request, 'home/lab_management_pages/experiment_dmp_report_page.html', {
            'page': self,
            'data': data,
            'sample_list': specialized_samples if specialized_samples else None,
            'instrument_list': instrument_list if instrument_list else None,
            'lab_dmp': lab_dmp if lab_dmp else None,
        })

# EASYDMP STUB TODO: dmp search page
class DMPSearchPage(Page): 
    pass

# EASYDMP STUB TODO: dmp view page
class DMPViewPage(Page): 
    pass

### THIS ARE STUB PAGES, MADE TO INTEGRATE INTO EPIRO. RIGHT NOW IGNORE THEM
class ProposalSubmissionPage(Page): # USER DATA DIMMT
    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
        max_length=255, help_text="Title text to use for the 'thank you' page")
    # Note that there's nothing here for specifying the actual form fields -
    # those are still defined in forms.py. There's no benefit to making these
    # editable within the Wagtail admin, since you'd need to make changes to
    # the code to make them work anyway.

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('thankyou_page_title'),
    ]

    def serve(self,request):
        if request.user.is_authenticated:
            username = request.user.username

        if request.method == 'POST':
            # If the method is POST, validate the data and perform a save() == INSERT VALUE INTO
            form = ProposalSubmissionForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                # BEWARE: This is a modelForm and not a object/model, "save" do not have some arguments of the same method, like using=db_tag
                # to work with a normal django object insert a line: data = form.save(commit=False) and then data is a basic model: e.g., you can use data.save(using=external_generic_db)
                # In our example the routing takes care of the external db save
                data = form.save(commit=False)
                data.proposal_id = proposal_id_generation(Users.objects.get(pk=username).affiliation)
                data.proposal_status = 'Submitted'
                if Users.objects.get(pk=username) is not None:
                    data.user_id = Users.objects.get(pk=username)
                
                #debug = data.proposal_filename

                data.save()
                return render(request, 'home/thank_you_proposal_page.html', {
                    'page': self,
                    # We pass the data to the thank you page, data.datavarchar and data.dataint!
                    'data': data,
                })
            else:
                #debug = form.errors
                return render(request, 'home/error_page.html', {
                        'page': self,
                        # We pass the data to the thank you page, data.datavarchar and data.dataint!
                        'errors': form.errors, # TODO: improve this
                    })

        else:
            #form = UserRegistrationForm()
            try:
                if Proposals.objects.get(pk=username) is not None:
                    form = ProposalSubmissionForm(instance=Proposals.objects.get(pk=username))
                else:
                    form = ProposalSubmissionForm()
            except Exception as e: # TODO Properly catch this
                form = ProposalSubmissionForm()


        return render(request, 'home/proposal_submission_page.html', {
                'page': self,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'data': form,
            })

class ProposalListPage(Page): # DIMMT
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    def serve(self,request):
        if request.user.is_authenticated:
            username = request.user.username
        if "filter" in request.GET:
            filter = request.GET.get("filter","")
        else:
            filter = ""
            request.GET = request.GET.copy()
            request.GET["filter"]= ""

        if request.method == 'POST':
            filter = request.POST.get("filter","")
            request.GET = request.GET.copy()
            request.GET["filter"] = request.POST.get("filter","")
        

        data = Proposals.objects.filter(user_id_id=request.user.username)
        data = data.filter(proposal_id__contains = filter)
        table = ProposalsTable(data)
        RequestConfig(request).configure(table)

        table.paginate(page=request.GET.get("page",1), per_page=25)
        return render(request, 'home/proposal_list.html', {
            'page': self,
            'table': table,
        })

class ServiceRequestSubmissionPage(Page): # DIMMT



    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
        max_length=255, help_text="Title text to use for the 'thank you' page")
    # Note that there's nothing here for specifying the actual form fields -
    # those are still defined in forms.py. There's no benefit to making these
    # editable within the Wagtail admin, since you'd need to make changes to
    # the code to make them work anyway.

    # drop down

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        #FieldPanel('Proposals', widget=forms.Select(choices=Proposals.objects.all().order_by('proposal_id'))),
        FieldPanel('thankyou_page_title'),
    ]

    def serve(self,request):

        if request.user.is_authenticated:
            username = request.user.username

        if "filter" in request.GET:
            filter = request.GET.get("filter","")
        else:
            filter = ""
            request.GET = request.GET.copy()
            request.GET["filter"]= filter

        if request.method == 'POST':
            filter = request.POST.get("filter","")
            request.GET = request.GET.copy()
            request.GET["filter"] = request.POST.get("filter","")
        

        dataQuery = Proposals.objects.filter(user_id=username)
        dataQuery = dataQuery.filter(proposal_id__contains = filter)
        table = ProposalsTable(dataQuery)
        RequestConfig(request).configure(table)
        table.paginate(page=request.GET.get("page",1), per_page=25)
        if request.method == 'POST':
            # If the method is POST, validate the data and perform a save() == INSERT VALUE INTO
            form = SRSubmissionForm(data=request.POST, user=username)
            if form.is_valid():
                # BEWARE: This is a modelForm and not a object/model, "save" do not have some arguments of the same method, like using=db_tag
                # to work with a normal django object insert a line: data = form.save(commit=False) and then data is a basic model: e.g., you can use data.save(using=external_generic_db)
                # In our example the routing takes care of the external db save
                data = form.save(commit=False)
                data.proposal_id = Proposals.objects.get(pk=request.POST.get('proposalId'))
                data.sr_id = sr_id_generation(proposal=data.proposal_id, lab=form.cleaned_data["lab_id"])
                data.sr_status = 'Submitted'
                
                #debug = data.proposal_filename

                data.save()
                return render(request, 'home/thank_you_sr_page.html', {
                    'page': self,
                    # We pass the data to the thank you page, data.datavarchar and data.dataint!
                    'data': data,
                })
            else:
                #debug = form.errors
                return render(request, 'home/error_page.html', {
                        'page': self,
                        # We pass the data to the thank you page, data.datavarchar and data.dataint!
                        'errors': form.errors, # TODO: improve this
                    })

        else:
            #form = UserRegistrationForm()
            try:
                if ServiceRequests.objects.get(pk=username) is not None:
                    form = SRSubmissionForm(instance=ServiceRequests.objects.get(pk=username), user=username)
                else:
                    form = SRSubmissionForm(user=username)
            except Exception as e: # TODO Properly catch this
                form = SRSubmissionForm(user=username)


        return render(request, 'home/sr_submission_page.html', {

                'page': self,
                'table': table,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'data': form,
                # keep the selection form open or not ("true" or "false")
            })
    
class NewTestPage(Page): # Test
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]