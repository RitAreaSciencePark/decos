from django import forms
# This import point to the external app schema!
from PRP_CDM_app.forms import FormsDefinition
from PRP_CDM_app.models import labDMP
from PRP_CDM_app.models import Users, Proposals, ServiceRequests, Laboratories, Samples, Instruments, Results
from PRP_CDM_app.fields import BooleanIfWhat, MultiChoicheAndOtherWidget


from django.contrib.auth.models import User, Group


class LabSwitchForm(forms.Form): 
    user_labs = []
    
    def _defineChoices(self):
        choices = []
        for user_lab in self.user_labs:
            choices.append((user_lab.name,user_lab.name))
        return choices

    def __init__(self, user_labs, *args, **kwargs):
        super(LabSwitchForm,self).__init__(*args, **kwargs)
        if user_labs is not None:
            self.user_labs = user_labs
            self.fields['lab_selected'] = forms.ChoiceField(choices=self._defineChoices())

# TODO: dynamic this
def form_orchestrator(user_lab, request, filerequest, getInstance):
    # lablist = [labform for labform in dir(FORMS()) if not labform.startswith("__")]
    if user_lab is None:
        return None # TODO manage this
    else:
        # this block checks the class names into FormsDefinition to create the forms
        formClass = getattr(FormsDefinition,user_lab.title() + "Form")
        if hasattr(formClass, "exclude") and formClass.exclude is not None:
            for formdef, values in formClass.exclude.items():
                pass # FIXME fix this ... or maybe not, investigate

        form_list = []
        # this block checks if there are some special field names to override the widgets
        widgets_list = {}
        for form_model in formClass.content:
            if hasattr(formClass, "exclude") and formClass.exclude is not None:
                exclude = formClass.exclude[form_model.__name__]
            if hasattr(form_model, "widgets") and form_model.widgets is not None:
                widgets_list = form_model.widgets
            if getInstance:
                instance = form_model.objects.get(pk=request.GET['sample_id'])
                request = None
            else:
                 instance = None

            form_list.append(form_factory(form_model, widgets_list, request=request, filerequest=filerequest, exclude_list=exclude, instance=instance))
        return form_list
 

def form_factory(form_model, widgets_list, request, filerequest, exclude_list, instance):
    class CustomForm(forms.ModelForm):

        # see https://docs.djangoproject.com/en/1.9/topics/forms/ for more complex example.
        # We are using a ModelForm, it is not mandatory
        
        class Meta:
            model = form_model
            # fields = ['datavarchar', 'dataint']
            debug = widgets_list
            widgets = widgets_list
            exclude = exclude_list

        def __init__(self, *args, **kwargs):
            super(CustomForm, self).__init__(*args, **kwargs)

    return CustomForm(request,filerequest, instance=instance)

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

class UserDataForm(forms.ModelForm):
    class Meta:
            model = Users
            # fields = ['datavarchar', 'dataint']
            '''widgets = {'gender': forms.SelectMultiple(),
                       'legal_status': forms.SelectMultiple(),
                       'research_role': forms.SelectMultiple(),
                       }'''
            exclude = ['user_id']

class InstrumentsForm(forms.ModelForm):

        # see https://docs.djangoproject.com/en/1.9/topics/forms/ for more complex example.
        # We are using a ModelForm, it is not mandatory
        
        class Meta:
            model = Instruments
            fields = ['vendor', 'model', 'description']

class ResultsForm(forms.ModelForm):
        
        # see https://docs.djangoproject.com/en/1.9/topics/forms/ for more complex example.
        # We are using a ModelForm, it is not mandatory
        
        class Meta:
            model = Results
            fields = ['main_repository', 'article_doi']


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
            
class AddNewLabForm(forms.ModelForm):
    class Meta:
            model = Laboratories
            fields = ['lab_id', 'description']


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
'''class LageSamplesForm(forms.ModelForm):
    class Meta:
        model = LageSamples
        exclude = ['sr_id',
                   'sample_id',
                   'sample_feasibility',
                   'sample_tatus']



class LameSamplesForm(forms.ModelForm):
    class Meta:
        model = LameSamples
        exclude = ['sr_id',
                   'sample_id',
                   'sample_feasibility',
                   'sample_tatus']'''

