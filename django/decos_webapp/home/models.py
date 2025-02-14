# Standard Library Imports
import json  # For handling JSON data
import logging  # For logging errors, warnings, and info
from os import listdir  # For listing files in a directory
from os.path import dirname, isfile, join  # For file path manipulations

# Third-party Imports (Django & Wagtail)
from django import forms  # For form handling
from django.conf import settings  # For accessing Django settings
from django.contrib.auth.models import Group, User  # User and Group models
from django.core.exceptions import ObjectDoesNotExist  # For handling non-existing objects
from django.db import connections, models  # ORM models and DB connections
from django.forms.models import model_to_dict  # For converting model instances to dictionaries
from django.shortcuts import redirect, render  # For rendering templates and handling redirects
from django.template.loader import render_to_string  # For rendering templates to strings
from django_tables2.config import RequestConfig  # For configuring table display

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
from decos_secrets import minIO_secrets  # Secrets configuration for minIO storage

from .decos_elab import Decos_Elab_API  # Integration with Decos Elab API
from .decos_jenkins import Decos_Jenkins_API  # Integration with Decos Jenkins API

from .forms import (  # Project-specific forms
    APITokenForm,
    DMPform,
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
    InstrumentsForResultsTable,
    ProposalsTable,
    ResultsTable,
    SamplesForResultsTable,
    SamplesTable,
    ServiceRequestTable,
)

from PRP_CDM_app.code_generation import (  # ID code generators for various entities
    instrument_id_generation,
    proposal_id_generation,
    result_id_generation,
    sample_id_generation,
    sr_id_generation,
    xid_code_generation,
)

from PRP_CDM_app.models import (  # Models related to samples, instruments, results, etc.
    LageSamples,
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
)

from APIs.decos_minio_API.decos_minio_API import decos_minio  # MinIO API integration

Group.add_to_class('laboratory', models.BooleanField(default=False))

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
    api_token = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="API Token",
        help_text="Optional token for authenticating API requests"
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

# SamplePage handles sample data entry for laboratories, extending the 'Samples' model.
# It integrates with lab models from 'decos_metadata_db' from 'PRP_CDM_app'.
class SamplePage(Page, SessionHandlerMixin):
    # Introductory text field
    intro = RichTextField(blank=True)
    # Title text for the thank-you page
    thankyou_page_title = RichTextField(blank=True)

    # Wagtail admin interface panels
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('thankyou_page_title'),
    ]

    # Creates and saves a Sample object from form data
    def _create_sample_from_form(self, form, lab, request):
        data = form.save(commit=False)
        sr_id_hidden = request.POST.get("sr_id_hidden")

        if sr_id_hidden and sr_id_hidden != 'internal':
            try:
                data.sr_id = ServiceRequests.objects.get(pk=sr_id_hidden)
            except ObjectDoesNotExist:
                raise ValueError(f"ServiceRequest with id {sr_id_hidden} does not exist.")

        data.sample_id = sample_id_generation(data.sr_id)
        data.lab_id = lab
        data.sample_status = 'Submitted'

        try:
            data.save()
            return data
        except Exception as e:
            logger.error(f"Failed to save sample: {e}")
            raise

    # Handles form submissions and creates samples
    def _handle_submission(self, request, lab):
        forms = form_orchestrator(
            user_lab=lab.lab_id, request=request.POST, filerequest=request.FILES, getInstance=False
        )

        saved_objects = []
        for form in forms:
            if not form.is_valid():
                return False, form.errors, forms

            sample = self._create_sample_from_form(form, lab, request)
            saved_objects.append(sample)

        return True, saved_objects, forms

    # Handles GET and POST requests for this page
    def serve(self, request):
        # Fetch lab from session; redirect if not set
        lab = self.get_lab_from_session(request)
        if not lab:
            request.session['return_page'] = request.get_full_path()
            return redirect('/switch-laboratory')

        sr_id = request.GET.get("sr_id", "internal")
        filter_term = request.GET.get("filter", "")

        if request.method == 'POST':
            success, result, forms = self._handle_submission(request, lab)
            if success:
                return render(request, 'home/thank_you_page.html', {'page': self, 'data': result})
            else:
                sr_id = request.POST.get("sr_id_hidden", "internal")
        else:
            forms = form_orchestrator(user_lab=lab.lab_id, request=None, filerequest=None, getInstance=False)

        # Fetch Service Requests filtered by lab and search term
        sr_query = ServiceRequests.objects.filter(lab_id=lab.lab_id)
        if filter_term:
            sr_query = sr_query.filter(sr_id__icontains=filter_term)

        sr_table = ServiceRequestTable(sr_query)
        RequestConfig(request).configure(sr_table)

        pageDict = {
            'page': self,
            'forms': forms,
            'lab': lab.lab_id,
            'sr_id': sr_id,
            'table': sr_table,
        }

        for form in forms:
            pageDict[form.Meta.model.__name__] = form
        pageDict['forms'] = forms

        # Attempt to load a lab-specific form template
        try:
            home_path = settings.BASE_DIR
            abs_path = join(home_path, 'home/templates/home/forms/')
            formlist = [f for f in listdir(abs_path)]
        except Exception as e:
            logger.error(f"Error loading form templates: {e}")
            formlist = []

        for formTemplate in formlist:
            if lab.lab_id.lower() in formTemplate.lower():
                return render(request, f'home/forms/{formTemplate}', pageDict)

        # Fallback to generic form template
        return render(request, 'home/forms/generic_form_page.html', pageDict)

    
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
            elab_api = Decos_Elab_API(ApiSettings.objects.get(pk=1).elab_base_url, token.elab_token)
            sample = Samples.objects.get(pk=sample_id)
            elab_api.create_new_decos_experiment(lab=lab, username=username, experiment_info=sample)
        except (ObjectDoesNotExist, UnboundLocalError) as e:
            logger.error(f"Elab submission failed: {e}")

    def _refresh_minio_samples(self, request, lab):
        # Updates sample locations from MinIO storage if requested.
        if request.POST.get('refresh') != 'true':
            return ""

        try:
            client = decos_minio(endpoint=minIO_secrets.endpoint, access_key=minIO_secrets.access_key, secret_key=minIO_secrets.secret_key)
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
            minIO_status = self._refresh_minio_samples(request, lab)

        samples = Samples.objects.filter(lab_id=lab.lab_id, sample_id__icontains=filter_term)
        table = SamplesTable(samples)
        RequestConfig(request).configure(table)
        table.paginate(page=request.GET.get('page', 1), per_page=5)

        return render(request, 'home/sample_pages/sample_list.html', {
            'page': self,
            'table': table,
            'minio_filelist_status': minIO_status,
        })

class EditSamplePage(Page): # EASYDMP
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    def serve(self,request):
        if request.user.is_authenticated:
            username = request.user.username
        
        if request.method == 'POST':
            sample = Samples.objects.get(pk = request.POST['sample_id_hidden'])
            lab = sample.lab_id
            # Dynamic form orchestrator (func that returns a factory that return the class form, why, 'cause django)
            # Check PRP_CDM_App form and models
            forms = form_orchestrator(user_lab=lab.lab_id, request=request.POST, filerequest=request.FILES, getInstance=False)

            for form in forms:
                if not form.is_valid():
                    return render(request, 'home/error_page.html', {
                        'page': self,
                        'errors': form.errors, # TODO: improve this
                    })
                else:
                    # Data is saved to db here
                    data = form.save(commit=False) # form data inserted here
                    # other info not in the form are inserted here ->
                    if(request.POST.get("sr_id_hidden") and (request.POST.get("sr_id_hidden") != 'internal')):
                        data.sr_id = ServiceRequests.objects.get(pk=request.POST.get("sr_id_hidden"))
                    data.sample_id = sample.sample_id
                    data.sample_location = sample.sample_location
                    data.lab_id = lab
                    data.sample_status = 'Submitted'
                    # final "TRUE" commit on db
                    data.save()
                    # Experiment created in elab, TODO: insert this in a better designed workflow
                    # TODO: Manage elab edits
            # Return thank you page html rendered page        
            return render(request, 'home/thank_you_page.html', {
                'page': self,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'data': data,
                })
        

        sample = Samples.objects.get(pk = request.GET['sample_id'])
        lab = sample.lab_id
        forms = form_orchestrator(user_lab=lab.lab_id, request=request, filerequest=None, getInstance=True)
            

        pageDict = {
            'page': self,
            'lab': lab.lab_id,
            'sr_id': sample.sr_id,
            'table': None,
            'sample_id': sample.sample_id
            }
        
        # every form could be created by multiple PRP_CDM_App tables, so we use "multiple forms"
        # one for every table, we put them in a list and visualize them in a linear layout (vertical)
        for form in forms:
            pageDict[form.Meta.model.__name__] = form
        pageDict['forms'] = forms
        formlist =[]
        # return the form page, with the form as data.
        # TODO: while using settings is correct, create/find another softcoded var!!
        try:
            home_path = settings.BASE_DIR
            abs_path = join(home_path,"home/templates/home/forms/")
            formlist = [f for f in listdir(abs_path)]
        except Exception as e:
            e # TODO: properly catch this

        for formTemplate in formlist:
            if pageDict['lab'].lower() in formTemplate:
                return render(request, 'home/forms/' + formTemplate, pageDict)
        else:
            return render(request, 'home/forms/generic_form_page.html', pageDict)

class PipelinesPage(Page): # EASYDMP
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    def serve(self, request):

        # TEST
        pipeline_name = "test_pipeline_with_parameters"
        secret_token = "parameter_test_pipeline_SECRET_TOKEN"

        #
        if request.user.is_authenticated:
            username = request.user.username
        # TODO: try me
        jenkins_client = Decos_Jenkins_API(username=username, lab=request.session.get('lab_selected'))

        if request.method == 'POST':
            sample_id = request.POST.get("pipelines",None)
            data = {"data0": sample_id,"data1": "DATA001"}
                # TODO: move JENKINS entrypoint to a dedicated page
            if sample_id:
                jenkins_client.start(sample_id=None, pipeline_name=pipeline_name, secret_token=secret_token, data=data)

        output = jenkins_client.get_pipeline_output(pipeline_name=pipeline_name)
        if request.GET.get("output", None):
            return render(request, 'home/sample_pages/pipelines_page.html', {
            'page': self,
            'sample_id': request.GET.get("pipelines",None),
            'console_output': output
        })
        return render(request, 'home/sample_pages/pipelines_page.html', {
            'page': self,
            'sample_id': request.GET.get("pipelines",None),
        })

class DMPPage(Page, SessionHandlerMixin): # EASYDMP
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

        if request.method == 'POST':
            # If the method is POST, validate the data and perform a save() == INSERT VALUE INTO
            form = DMPform(data=request.POST)
            if form.is_valid():
                # BEWARE: This is a modelForm and not a object/model, "save" do not have some arguments of the same method, like using=db_tag
                # to work with a normal django object insert a line: data = form.save(commit=False) and then data is a basic model: e.g., you can use data.save(using=external_generic_db)
                # In our example the routing takes care of the external db save
                data = form.save(commit=False)
                data.lab_id = request.session["lab_selected"]
                data.user_id = username
                data.save()
                return render(request, 'home/dmp_pages/labdmp_page.html', {
                    'page': self,
                    # We pass the data to the thank you page, data.datavarchar and data.dataint!
                    'data': form,
                    'lab': self.get_lab_from_session(request),
                })
            else:
                return render(request, 'home/error_page.html', {
                        'page': self,
                        # We pass the data to the thank you page, data.datavarchar and data.dataint!
                        'errors': form.errors, # TODO: improve this
                    })

        else:
            try:
                if labDMP.objects.get(pk=request.session["lab_selected"]) is not None:
                    form = DMPform(instance=labDMP.objects.get(pk=request.session["lab_selected"]))
                else:
                    form = DMPform()
            except Exception as e: # TODO Properly catch this
                form = DMPform()

        return render(request, 'home/dmp_pages/labdmp_page.html', {
                'page': self,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'data': form,
                'lab': request.session['lab_selected'],
            })

class DMPSearchPage(Page): # EASYDMP
    pass

class DMPViewPage(Page): #EASYDMP # TODO: implement this page
    pass

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

class ResultsPage(Page, SessionHandlerMixin):
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
            if(self.get_lab_from_session(request) is None):
                request.session["return_page"] = request.META['HTTP_REFERER']
                next = request.POST.get("next", "/switch-laboratory")
                return redirect(next)
        except KeyError:
            request.session["return_page"] = request.META['HTTP_REFERER']
            next = request.POST.get("next", "/switch-laboratory")
            return redirect(next)
        
        lab = request.session['lab_selected']

        sample_list = []
        if "sample_list" in request.GET:
            sample_list =request.GET.get('sample_list','')
            if sample_list != "":
                sample_list = json.loads(sample_list)
        if "sample_id" in request.GET:
            sample_id = request.GET.get("sample_id","")
            if sample_id != "" and sample_id != 'public':
                    sample_list.append(sample_id)

        public_dataset_list = []
        if "public_dataset_list" in request.GET:
            public_dataset_list =request.GET.get('public_dataset_list','')
            if public_dataset_list != "[]":
                public_dataset_list = json.loads(public_dataset_list)
            else:
                public_dataset_list = []
        if "public_dataset_location" in request.GET:
            public_dataset_location = request.GET.get("public_dataset_location","")
            if public_dataset_location != "":
                public_dataset_list.append(public_dataset_location)


        instrument_list = []
        if "instrument_list" in request.GET:
            instrument_list =request.GET.get('instrument_list','')
            if instrument_list != "":
                instrument_list = json.loads(instrument_list)
        if "instrument_id" in request.GET:
            instrument_id = request.GET.get("instrument_id","")
            if instrument_id != "":
                instrument_list.append(instrument_id)

        software_list = []
        if "software_list" in request.GET:
            software_list =request.GET.get('software_list','')
            if software_list != "":
                software_list = json.loads(software_list)
        if "software_id" in request.GET:
            software_id = request.GET.get("software_id","")
            if software_id != "":
                software_list.append(software_id)


        if request.method == 'POST':
            # If the method is POST, validate the data and perform a save() == INSERT VALUE INTO
            form = ResultsForm(data=request.POST)
            if form.is_valid():
                # BEWARE: This is a modelForm and not a object/model, "save" do not have some arguments of the same method, like using=db_tag
                # to work with a normal django object insert a line: data = form.save(commit=False) and then data is a basic model: e.g., you can use data.save(using=external_generic_db)
                # In our example the routing takes care of the external db save
                data = form.save(commit=False)
                result_id = result_id_generation(data) # NOTE: for now it is a UUID
                data.result_id = result_id
                data.save()
            # TODO: check uniqueness on doi, and so on
                result = Results.objects.get(pk = result_id)
                for sample in sample_list:
                    sample = Samples.objects.get(pk = sample)
                    ResultxSample.objects.get_or_create(x_id = xid_code_generation(result_id,sample.sample_id), results = result, samples = sample)

                
                for instrument in instrument_list:
                    instrument = Instruments.objects.get(pk = instrument)
                    ResultxInstrument.objects.get_or_create(x_id = xid_code_generation(result_id,instrument.instrument_id), results = result, instruments = instrument)

                
                # data.save()
                # data.lab_id = request.session["lab_selected"]
                # data.user_id = username
                # data.save()
                return render(request, 'home/thank_you_page.html', {
                'page': self,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'data': data,
                })
            else:
                return render(request, 'home/error_page.html', {
                        'page': self,
                        # We pass the data to the thank you page, data.datavarchar and data.dataint!
                        'errors': form.errors, # TODO: improve this
                    })

                # first sample filter selection dropdown ->
        if "sample_filter" in request.GET:
            sample_filter = request.GET.get("sample_filter","")
            if sample_filter != "" :
                sample_filter_set = "open "
            else:
                sample_filter_set = " "
        else:
            sample_filter = ""
            request.GET = request.GET.copy()
            request.GET["sample_filter"]= ""
            sample_filter_set = " "



                # first sample filter selection dropdown ->
        if "instrument_filter" in request.GET:
            instrument_filter = request.GET.get("instrument_filter","")
            if instrument_filter != "" :
                instrument_filter_set = "open "
            else:
                instrument_filter_set = " "
        else:
            instrument_filter = ""
            request.GET = request.GET.copy()
            request.GET["instrument_filter"]= ""
            instrument_filter_set = " "


        # REPORTS
        article_doi = request.GET.get("article_doi","")
        main_repository = request.GET.get("main_repository","")
    
        # SAMPLES
        # Dropdown for Samples requests --> 
        # check the Samples request in the dropdown
        dataQuery = Samples.objects.filter(lab_id=lab)
        dataQuery = dataQuery.filter(sample_id__contains = sample_filter)
        sample_table = SamplesForResultsTable(dataQuery,prefix="sample_")
        RequestConfig(request).configure(sample_table)
        sample_table.paginate(page=request.GET.get("sample_page",1), per_page=5) # TODO: implement dynamic per page settings?
        
        if "sample_page" in request.GET:
            sample_page = request.GET.get("sample_page","")
            if sample_page != "" :
                sample_filter_set = "open "
            else:
                sample_filter_set = " "

        # INSTRUMENTS
        # Dropdown for Instruments requests --> 
        # check the Instruments request in the dropdown
        # dataQuery = Instruments.objects.filter(lab_id=lab)
        dataQuery = Instruments.objects.filter(instrument_id__contains = instrument_filter)
        instrument_table = InstrumentsForResultsTable(dataQuery,prefix="inst_")
        RequestConfig(request).configure(instrument_table)
        instrument_table.paginate(page=request.GET.get("inst_page",1), per_page=5) # TODO: implement dynamic per page settings?
        
        if "inst_page" in request.GET:
            inst_page = request.GET.get("inst_page","")
            if inst_page != "" :
                instrument_filter_set = "open "
            else:
                instrument_filter_set = " "

        pageDict = {
            'page': self,
            'lab': lab,
            'article_doi': article_doi,
            'main_repository': main_repository,            
            'sample_table': sample_table,
            'sample_filter' : sample_filter_set,
            'instrument_filter' : instrument_filter_set,
            'sample_list' : json.dumps(sample_list),
            'sample_list_view' : sample_list,
            'public_dataset_list' : json.dumps(public_dataset_list),
            'public_dataset_list_view' : public_dataset_list,
            'instruments_table' : instrument_table,
            'instrument_list' : json.dumps(instrument_list),
            'instrument_list_view' : instrument_list,
            'software_list' : json.dumps(software_list),
            'software_list_view' : software_list,
            }

        


        return render(request, 'home/lab_management_pages/results_page.html', pageDict)

class ResultsListPage(Page): # EASYDMP 
    
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    def serve(self,request):
        if request.user.is_authenticated:
            username = request.user.username
        
        try:
            if(request.session['lab_selected'] is None):
                request.session["return_page"] = request.META['HTTP_REFERER']
                next = request.POST.get("next", "/switch-laboratory")
                return redirect(next)
            else:
                lab = Laboratories.objects.get(pk = request.session['lab_selected'])
        except KeyError:
            request.session["return_page"] = request.META['HTTP_REFERER']
            next = request.POST.get("next", "/switch-laboratory")
            return redirect(next)

            # JENKINS
            # TODO: Add a callback or a initial timer
        '''
        try:
            jenkins_api = Decos_Jenkins_API(username=username, lab=lab)
            if jenkins_filelist_status is None:
                jenkins_filelist_status = 'Waiting'
            else:
                if request.POST['list_folders'] == 'true':
                    jenkins_filelist_status = jenkins_api.get_latest_build(f"test_Folder/job/folderList")['result']
                    jenkins_api.build_job(job_path= f"test_Folder/job/folderList", secret_token="folderList_SECRET_TOKEN")
                    jenkins_filelist_status = 'Sent'

        except Exception as e: # TODO: catch and manage this
            print(f"error on jenkins_api: {e}") 
        '''
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

        # FIXME: put a lab_id in the model or something else!
        # data = Results.objects.filter(lab_id=request.session.get('lab_selected'))
        data = Results.objects.all()
        data = data.filter(result_id__contains = filter)
        table = ResultsTable(data)
        RequestConfig(request).configure(table)

        table.paginate(page=request.GET.get("page",1), per_page=5) # TODO: softcode paginate settings
        return render(request, 'home/lab_management_pages/results_list_page.html', {
            'page': self,
            'table': table,
        })

class ExperimentDMPPage(Page):
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    def serve(self,request):
        if request.user.is_authenticated:
            username = request.user.username
        
        try:
            if(request.session['lab_selected'] is None):
                request.session["return_page"] = request.META['HTTP_REFERER']
                next = request.POST.get("next", "/switch-laboratory")
                return redirect(next)
            else:
                lab = Laboratories.objects.get(pk = request.session['lab_selected'])
        except KeyError:
            request.session["return_page"] = request.META['HTTP_REFERER']
            next = request.POST.get("next", "/switch-laboratory")
            return redirect(next)
        
        result_id = request.GET.get("result_id","")
        if result_id != "":
            data = Results.objects.get(pk = result_id)
            sample_x_list = ResultxSample.objects.filter(results = data)
            sample_list = []
            for sample in sample_x_list:
                sample = Samples.objects.get(pk = sample.samples_id)
                # TODO: dynamic this -> hasattr and so on and match
                if(sample.lab_id.lab_id == 'LAGE'):
                    sample = LageSamples.objects.get(pk = sample.sample_id)
                else:
                    pass # TODO: implement other labs
                sample_list.append(sample)
            instrument_x_list = ResultxInstrument.objects.filter(results = data)
            instrument_list = []
            for instrument in instrument_x_list:
                instrument = Instruments.objects.get(pk = instrument.instruments.instrument_id)
                instrument_list.append(instrument)

            try:
                lab_dmp = labDMP.objects.get(pk = request.session['lab_selected'])
            except labDMP.DoesNotExist as e:
                lab_dmp = None


        
        return render(request, 'home/lab_management_pages/dmp_page.html', {
            'page': self,
            'data': data,
            'sample_list': sample_list,
            'instrument_list': instrument_list,
            'lab_dmp': lab_dmp,
        })

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
    