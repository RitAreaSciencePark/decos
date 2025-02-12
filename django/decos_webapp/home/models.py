# FIXME: put this into the API_TOKENS
from decos_secrets import minIO_secrets

# modules implemented in the container! In case you see red
from django.db import models, connections
from .secrets_models import API_Tokens

### wagtail imports
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
### end wagtail imports

### django forms imports with PRP_CMD
from django.conf import settings
from django.shortcuts import render, redirect
from django import forms
from django.forms.models import model_to_dict
from django.contrib.auth.models import User, Group

from .forms import form_orchestrator, LabSwitchForm, DMPform, UserDataForm, APITokenForm, ProposalSubmissionForm, SRSubmissionForm, InstrumentsForm, ResultsForm #, LageSamplesForm, LameSamplesForm

from PRP_CDM_app.models import labDMP, Users, Proposals, ServiceRequests, Laboratories, Samples, Instruments, Results, ResultxSample, ResultxInstrument
from PRP_CDM_app.models import LabXInstrument, LageSamples

from django.template.loader import render_to_string
# TODO: use it or not, decide: from PRP_CDM_app.reports import ReportDefinition 
### end django forms imports with PRP_CDM

### file system import, mainly for file attachments
from os import listdir
from os.path import isfile,join,dirname
###

### Id generators
# FIXME: is this used? from uuid import uuid4
from PRP_CDM_app.code_generation import sr_id_generation, proposal_id_generation, sample_id_generation, instrument_id_generation, result_id_generation, xid_code_generation
### end Id generators

### dynamic tables for reporting 
from .tables import ProposalsTable,ServiceRequestTable,SamplesTable, SamplesForResultsTable, InstrumentsForResultsTable, ResultsTable
from django_tables2.config import RequestConfig
### end dynamic tables for reporting 

import json

### APIs
from .decos_elab import Decos_Elab_API
from .decos_jenkins import Decos_Jenkins_API
from APIs.decos_minio_API.decos_minio_API import decos_minio
### end APIs

# TODO: MAYBE ABC? implement Abstract classes and methods could be useful in this page.

# FIXME: the first character of the widget when recovered do not appear. Editsamples
# FIXME: I frankly do not remember what does the next line does: so, good luck.
Group.add_to_class('laboratory', models.BooleanField(default=False))

from django.core.exceptions import ObjectDoesNotExist


@register_setting # Settings in admin page
class HeaderSettings(BaseGenericSetting):
    header_text = RichTextField(blank=True)
    prp_icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("prp_icon"),
                FieldPanel("header_text"),
            ],
            "Header Static",
        )
    ]

@register_setting
class FooterSettings(BaseGenericSetting):

    footer_text = RichTextField(blank=True)
    github_url = models.URLField(verbose_name="GitHub URL", blank=True)
    github_icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel("footer_text"),
        MultiFieldPanel(
            [
                FieldPanel("github_url"),
                FieldPanel("github_icon"),
            ],
            "Footer Links",
        )
    ]

@register_setting
class ApiSettings(BaseGenericSetting): # TODO: Implement this, it is now hardcoded!
    # FIXME: FIX FOR MULTIPLE LABS!  
    elab_base_url = models.URLField(verbose_name = "elab url", blank=True)
    jenkins_base_url = models.URLField(verbose_name="jenkins url", blank = True)
    
    panels = [
        FieldPanel("elab_base_url"),
        FieldPanel("jenkins_base_url"),
    ]

# template: file://./templates/home/home_page.html
class HomePage(Page):
    intro = models.CharField(max_length=250, default="")
    body = RichTextField(blank=True)
    content_panels = [
    FieldPanel("title"),
    FieldPanel("intro"),
    FieldPanel("body"),
    ]

# template: file://./templates/home/home_page.html
class SwitchLabPage(Page):
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def serve(self, request):
        if request.user.is_authenticated:
            username = request.user.username

        if request.method == 'POST':
            # If the method is POST, validate the data and perform a save() == INSERT VALUE INTO
            form = LabSwitchForm(data=request.POST, user_labs=request.user.groups.filter(laboratory=True))
            if form.is_valid():
                # BEWARE: This is a modelForm and not a object/model, "save" do not have some arguments of the same method, like using=db_tag
                # to work with a normal django object insert a line: data = form.save(commit=False) and then data is a basic model: e.g., you can use data.save(using=external_generic_db)
                # In our example the routing takes care of the external db save
                laboratory = form.cleaned_data.get('lab_selected')
                request.session["lab_selected"] = laboratory
                try:
                    return redirect(request.session["return_page"])  # FIXME: Not working as intended
                except:
                    return redirect('/')
        else:
            try:
                request.session["return_page"] = request.META['HTTP_REFERER']
            except KeyError:
                request.session["return_page"] = "/"
            
            debug = request.user.groups.all()
            if not request.user.groups.all():
                return render(request, 'home/error_page.html', {
                'page': self,
                'errors': {"No assigned laboratory":"The User has no assigned laboratory, contact the administrator."}, # TODO: improve this
                })
            form = LabSwitchForm(user_labs=request.user.groups.filter(laboratory=True))
        debug = form
        renderPage = render(request, 'switch_lab.html', {
                'page': self,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'data': form,
            })
        return renderPage

class UserDataPage(Page):
    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
        max_length=255, help_text="Title text to use for the 'thank you' page")
    # Note that there's nothing here for specifying the actual form fields -
    # those are still defined in forms.py. There's no benefit to making these
    # editable within the Wagtail admin, since you'd need to make changes to
    # the code to make them work anyway.
    # regardless, a little bit of customization for the page, as title and intros,
    # are a good thing

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('thankyou_page_title'),
    ]

    def serve(self,request):
        if request.user.is_authenticated:
            username = request.user.username

        if request.method == 'POST':
            # If the method is POST, validate the data and perform a save() == INSERT VALUE INTO
            debug = request.POST
            form_user = UserDataForm(data=request.POST)
            if form_user.is_valid():
                # BEWARE: This is a modelForm and not a object/model, "save" do not have some arguments of the same method, like using=db_tag
                # to work with a normal django object insert a line: data = form.save(commit=False) and then data is a basic model: e.g., you can use data.save(using=external_generic_db)
                # In our example the routing takes care of the external db save
                data = form_user.save(commit=False)
                #data.lab_id = request.session["lab_selected"]
                data.user_id = username
                data.save()
            form_api_tokens = APITokenForm(data=request.POST, username=username)
            try:
                if form_api_tokens['laboratory'].data != '':
                    lab = form_api_tokens['laboratory'].data
                    # elab_token = form_api_tokens['elab_token'].data
                    # jenkins_token = form_api_tokens['jenkins_token'].data
                    data = form_api_tokens.save(commit=False)
                    # this block is to update only the fields actually written on, TODO: api token check? Low priority
                    if form_api_tokens.is_valid() and lab != '':
                        debug = form_api_tokens["laboratory"].data

                        lab = Laboratories.objects.get(pk=form_api_tokens["laboratory"].data)
                        api_token_queryset = API_Tokens.objects.filter(laboratory = lab, user_id = User.objects.get(username=username))
                        # api_token_queryset = API_Tokens.objects.all()
                        if api_token_queryset.values().count() > 0:
                            data.id = api_token_queryset.first().id
                            debug = form_api_tokens['elab_token'].data
                            if form_api_tokens['elab_token'].data == '':
                                data.elab_token = api_token_queryset.values('elab_token').first()['elab_token']
                            if form_api_tokens['jenkins_token'].data == '':
                                data.jenkins_token = api_token_queryset.values('jenkins_token').first()['jenkins_token']

                        data.user_id = User.objects.get(username=username)
        
                        data.save()
                        return render(request, 'home/utility_pages/user_data_page.html', {
                        'page': self,
                        # We pass the data to the thank you page, data.datavarchar and data.dataint!
                        'user_data': form_user,
                        'api_token_data': form_api_tokens,
                    })
                else:
                    return render(request, 'home/utility_pages/user_data_page.html', {
                    'page': self,
                    # We pass the data to the thank you page, data.datavarchar and data.dataint!
                    'user_data': form_user,
                    'api_token_data': APITokenForm(username=username),
                })
            except KeyError as e:
                pass
                
            
            else:
                return render(request, 'home/error_page.html', {
                        'page': self,
                        # We pass the data to the thank you page, data.datavarchar and data.dataint!
                        'errors': form.errors, # TODO: improve this
                    })
        else:
            #form = UserRegistrationForm()
            try:
                if Users.objects.get(pk=username) is not None:
                    form_user = UserDataForm(instance=Users.objects.get(pk=username))
                else:
                    form_user = UserDataForm()
            except Exception as e: # TODO Properly catch this
                form_user = UserDataForm()

        form_api_tokens = APITokenForm(username=username)

        return render(request, 'home/utility_pages/user_data_page.html', {
                'page': self,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'user_data': form_user,
                'api_token_data': form_api_tokens,
            })

class SamplePage(Page): # EASYDMP / DIMMT?
    # Just a little bit of customization
    intro = RichTextField(blank=True)
    thankyou_page_title = models.CharField(
    max_length=255, help_text="Title text to use for the 'thank you' page")
       
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('thankyou_page_title'),
        ]
    # Real page forms is served here:
    def serve(self, request):

        if request.user.is_authenticated:
            username = request.user.username
        
        # first service request selection dropdown ->
        if "filter" in request.GET:
            filter = request.GET.get("filter","")
        else:
            filter = ""
            request.GET = request.GET.copy()
            request.GET["filter"]= ""

        if request.method == 'POST': #???
            filter = request.POST.get("filter","")
            request.GET = request.GET.copy()
            request.GET["filter"] = request.POST.get("filter","")
        
        if(request.GET.get("sr_id") and request.GET.get("sr_id") != "internal"):
           sr_id = request.GET.get("sr_id")
           sr = ServiceRequests.objects.get(sr_id = sr_id)
        else:
            sr_id = "internal"
            sr = None
        # <- end selection here

        # lab selected is retrieved from session
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
        

        if request.method == 'POST':
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
                    data.sample_id = sample_id_generation(data.sr_id)
                    data.lab_id = lab
                    data.sample_status = 'Submitted'
                    # final "TRUE" commit on db
                    data.save()
                    # Experiment created in elab, TODO: insert this in a better designed workflow

            # Return thank you page html rendered page        
            return render(request, 'home/thank_you_page.html', {
                'page': self,
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'data': data,
                })
        else:
            forms = form_orchestrator(user_lab=lab.lab_id, request=None, filerequest=None, getInstance=False)
        
        # Dropdown for service requests --> 
        # check the service request in the dropdown
        dataQuery = ServiceRequests.objects.filter(lab_id=lab.lab_id)
        dataQuery = dataQuery.filter(sr_id__contains = filter)
        table = ServiceRequestTable(dataQuery)
        RequestConfig(request).configure(table)
        table.paginate(page=request.GET.get("page",1), per_page=5) # TODO: implement dynamic per page settings?
        pageDict = {
            'page': self,
            'lab': lab.lab_id,
            'sr_id': sr_id,
            'table': table,
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

        # Serve the form template in ./home/forms/ if present, if not, return render
        for formTemplate in formlist:
            if pageDict['lab'].lower() in formTemplate:
                return render(request, 'home/forms/' + formTemplate, pageDict)
        return render(request, 'home/forms/generic_form_page.html', pageDict)

class SampleListPage(Page): # EASYDMP 
    
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

        minIO_status = ""

        if request.method == 'POST':
            filter = request.POST.get("filter","")
            request.GET = request.GET.copy()
            request.GET["filter"] = request.POST.get("filter","")
            elab_write = request.POST.get("elab_write",None)
            if elab_write:
                # TODO: ElabWrite
                try:
                    tokens = API_Tokens.objects.filter(laboratory=lab.lab_id,user_id=User.objects.get(username = username))
                    token = tokens.first()

                    elab_api = Decos_Elab_API(ApiSettings.objects.get(pk = 1).elab_base_url,token.elab_token)
                except ObjectDoesNotExist as e:
                    return render(request, 'home/error_page.html', {
                        'page': self,
                        'errors': e, # TODO: improve this
                    })
                sample = Samples.objects.get(pk = request.POST['elab_write'])

                try:
                    elab_api.create_new_decos_experiment(lab=lab,username=username,experiment_info=sample)
                except UnboundLocalError as e:
                    pass
                    print( " Elab api ") # TODO: catch this better!

            try: # TODO: MAKE IT NOT HARDCODED!
                # MINIO
                debug = request.POST.get("refresh")
                if request.POST.get("refresh","false") == "true":
                    try:
                        client = decos_minio(endpoint=minIO_secrets.endpoint, access_key=minIO_secrets.access_key,
                                            secret_key=minIO_secrets.secret_key)
                        data_locations = client.get_sample_list(lab=lab)
                        minIO_status = "minIO buckets read correctly"
                    except Exception as e:
                        # TODO properly catch this and manage logging/debugging verbosity
                        minIO_status = f"Error on MinIO: {e}"

                    samples = Samples.objects.filter(lab_id = request.session['lab_selected'])


                    for sample in samples:
                        try:
                            sample = Samples.objects.get(pk = sample.sample_id)
                            for sample_id, sample_location in data_locations:
                                if sample.pk == sample_id:
                                    sample.sample_location = sample_location.object_name
                                    break
                                else:
                                    sample.sample_location = None
                            sample.save()
                        except Samples.DoesNotExist as e:
                            print("Debug: {e}") # TODO: properly manage this, TODO: implement a log library?
                       
                '''sample_list = []
                for sample_id, sample_location in data_locations:
                    try:
                        sample = (Samples.objects.get(pk = sample_id))
                        sample.sample_location = "/"+sample_location
                        sample.save()
                    except Samples.DoesNotExist as e:
                        print("Debug: {e}") # TODO: properly manage this, TODO: implement a log library?
                        ''' #TODO: IMPLEMENT ME NOW!
            except Exception as e: # FIXME: properly catch
                print(f"debug: {e}")
        
        data = Samples.objects.filter(lab_id=request.session.get('lab_selected'))
        data = data.filter(sample_id__contains = filter)
        table = SamplesTable(data)
        RequestConfig(request).configure(table)

        table.paginate(page=request.GET.get("page",1), per_page=5) # TODO: softcode paginate settings
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

class DMPPage(Page): # EASYDMP
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
                    'lab': request.session['lab_selected'],
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
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]

    def serve(self,request):
        if request.user.is_authenticated:
            username = request.user.username
        
        try: # TODO: optimize this
            if(request.session['lab_selected'] is None):
                request.session["return_page"] = request.META['HTTP_REFERER']
                next = request.POST.get("next", "/switch-laboratory")
                return redirect(next)
        except KeyError: # FIXME: Fix the HTTP_REFERER Not present! 
            request.session["return_page"] = request.META['HTTP_REFERER']
            next = request.POST.get("next", "/switch-laboratory")
            return redirect(next)
        
        def pkSelection(modelTable, pk):
            return modelTable.objects.get(pk=pk)
        
        def reportOrchestrator(user_lab):
        # lablist = [labform for labform in dir(FORMS()) if not labform.startswith("__")]
            if user_lab is None:
                return None # TODO manage this
            else:
                # this block checks the class names into FormsDefinition to create the forms
                reportClass = getattr(ReportDefinition,user_lab.title() + "Report")
                return reportClass.content
        
        reportList = []
        if request.method == 'POST':
            for report in reportOrchestrator(user_lab=request.session['lab_selected']):
                reportList.append(pkSelection(modelTable=report, pk=request.POST.get('sr_id')))
                pass
        else:
            try:
                for report in reportOrchestrator(user_lab=request.session['lab_selected']):
                    reportList.append(pkSelection(modelTable=report, pk=request.session["sr_id"]))
            except:
                return redirect('/')

        pageDict = {
            'page': self,
            'lab': request.session['lab_selected'],
            }

        reports = {}
        for fields in reportList:
            pageDict[type(fields).__name__] = (model_to_dict(fields))
            reports[type(fields).__name__] = (model_to_dict(fields))
        
        pageDict['reports'] = reports

        # return the form page, with the form as data.
        # TODO: while using settings is correct, create/find another softcoded var!!
        try:
            home_path = settings.BASE_DIR
            abs_path = join(home_path,"home/templates/home/reports/")
            reportlist = [f for f in listdir(abs_path)]
        except Exception as e:
            e # TODO: properly catch this

        for reportTemplate in reportlist:
            if pageDict['lab'].lower() in reportTemplate:
                return render(request, 'home/reports/' + reportTemplate, pageDict)
        return render(request, 'home/generic_dmp_view.html', pageDict)

class InstrumentsPage(Page): # EASYDMP
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

class ResultsPage(Page):
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
    