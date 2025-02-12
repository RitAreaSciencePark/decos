from django.db import models
# This apps is reserved to create the models of our external database schema
# through django ORM
from django import forms
from uuid import uuid4
from .fields import MultiChoicheAndOtherWidget, BooleanIfWhat
import datetime
import json
import os
from pathlib import Path

# FIXME: IMPORTANT, REFACTOR THE SCHEMA WITH BETTER columns NAMES! (e.g. remove [..]_id_id for fk...)

# NOTE: For "multiple choices + free text fields"
# in this version they must be declared like this:
#    test_choices = (
#        ("A","A"),
#        ("B","B"),
#    )
#    test = models.CharField(blank=True)
#    widgets = {"test": MultiChoicheAndOtherWidget(choices=test_choices),}
# NOTE: If multiple choices without free text field, use:
#     test = models.CharField(choices=test_choices)

def initChoices():
    path = Path(__file__).parent / "choices.json"
    with path.open() as f:
        d = json.load(f)            
        return d
    
choices = initChoices()

def tupleConvert(shortList):
    outlist = []
    for item in shortList:
        outlist.append((item[0],item[1]))
    return outlist

class Users(models.Model):
    user_id = models.CharField(max_length=50, primary_key=True)
    name_surname = models.CharField(max_length=50)
    email = models.CharField(max_length=128)
    affiliation = models.CharField(max_length=128)
    userchoices = choices["Users"]
    gender_choices = tupleConvert(userchoices["gender_choices"])
    gender = models.CharField(choices=gender_choices)
    legal_status_choices = tupleConvert(userchoices["legal_status_choices"])
    legal_status = models.CharField(choices=legal_status_choices, blank=True, null=True)
    research_role_choices = tupleConvert(userchoices["research_role_choices"])
    research_role = models.CharField(choices=research_role_choices)
    
    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'users'.lower()

class Laboratories(models.Model):
    lab_id = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=50)
    # user_id_responsible = models.ForeignKey(Users, on_delete=models.PROTECT)
    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    def __str__(self):
        return self.lab_id
    
    class Meta:
        db_table= 'laboratories'.lower()

class Proposals(models.Model):
    proposal_id = models.CharField(max_length=50, primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.PROTECT)
    proposal_status = models.CharField(default='Submitted')
    proposalschoices = choices["Proposals"]
    proposal_feasibility_choices = tupleConvert(proposalschoices["proposal_feasibility_choices"])
    proposal_feasibility = models.CharField(choices=proposal_feasibility_choices,blank=True)
    proposal_date = models.DateField(blank=False, default=datetime.date.today)
    
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'uploads/proposals/{0}/{1}'.format(instance.user_id.user_id, filename)

    proposal_filename = models.FileField(blank=True, upload_to=user_directory_path)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'proposals'.lower()

class ServiceRequests(models.Model):
    sr_id = models.CharField(max_length=50, primary_key=True)
    proposal_id = models.ForeignKey(Proposals, on_delete=models.PROTECT)
    lab_id = models.ForeignKey(Laboratories, on_delete=models.PROTECT)
    sr_status = models.CharField(default='Submitted')
    exp_description = models.TextField(max_length=500, blank=True)
    output_delivery_date = models.DateField(blank=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'service_requests'.lower()

class Samples(models.Model):
    #widgets = {}
    sample_id = models.CharField(max_length=50, primary_key=True)
    sr_id = models.ForeignKey(ServiceRequests, on_delete=models.PROTECT, null=True)
    lab_id = models.ForeignKey(Laboratories, on_delete=models.PROTECT)
    sample_short_description = models.CharField(max_length=64)
    sample_description = models.TextField(max_length=500, blank=True)
    samples_choices = choices["Samples"]
    sample_feasibility_choices = samples_choices["sample_feasibility_choices"]
    sample_feasibility = models.CharField(choices=sample_feasibility_choices, blank=True)
    #widgets["sr_feasibility"] = MultiChoicheAndOtherWidget(choices=sample_feasibility_choices)
    sample_status = models.CharField(default='Submitted')
    sample_location = models.CharField(blank=True, null=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'samples'.lower()

class LageSamples(Samples):
    widgets = {}
    lagesamples_choices = choices["LageSamples"]
    type_choices = tupleConvert(lagesamples_choices["type_choices"])
    type = models.CharField(blank=True)
    widgets["type"] = MultiChoicheAndOtherWidget(choices=type_choices)
    #sample_id = models.CharField(max_length=50, primary_key=True) # also FK table samples
    is_volume_in_ul = models.CharField(blank=True)
    widgets["is_volume_in_ul"] = BooleanIfWhat(yes_or_no=False)
    is_buffer_used = models.CharField(blank=True)
    widgets["is_buffer_used"] = BooleanIfWhat(yes_or_no=False)
    is_quality = models.CharField(blank=True)
    widgets["is_quality"] = BooleanIfWhat(yes_or_no=False)
    sample_date_of_delivery = models.DateField(blank=False)
    sample_back = models.BooleanField()
    reagents_provided_by_client = models.BooleanField()
    reagents_date_of_delivery = models.DateField(blank=True, null=True)
    
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        if(instance.sr_id):
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.sr_id.sr_id, instance.sample_id, filename)
        else:
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.lab_id, instance.sample_id, filename)

    sample_sheet_filename = models.FileField(blank=True, upload_to=user_directory_path)
    additional_filename = models.FileField(blank=True, upload_to=user_directory_path)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'lage_samples'.lower()

class LameSamples(Samples):
    chemical_formula = models.CharField(blank=True)
    elements_list = models.CharField(blank=True)
    sample_date_of_delivery = models.DateField()
    sample_back = models.BooleanField()
    
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'uploads/samples/{0}/{1}/{2}'.format(instance.sr_id.sr_id, instance.sample_id, filename)

    sample_sheet_filename = models.FileField(blank=True, upload_to=user_directory_path)
    additional_filename = models.FileField(blank=True, upload_to=user_directory_path)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'lame_samples'.lower()

class Instruments(models.Model):
    # TODO: put lab_id or put this in Laboratories
    instrument_id = models.CharField(max_length=50, primary_key=True)
    vendor = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    description = models.CharField(max_length=50, blank=True)
    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'instruments'.lower()

class Techniques(models.Model):
    technique_id = models.CharField(max_length=50, primary_key=True)
    technique_name = models.CharField(max_length=50)
    description = models.CharField(max_length=50, blank=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'techniques'.lower()

class InstrumentXTechnique(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    instrument_id = models.ForeignKey(Instruments, on_delete=models.PROTECT)
    technique_id = models.ForeignKey(Techniques, on_delete=models.PROTECT)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'instrument_x_technique'.lower()

class LabXInstrument(models.Model):
    # x_id = models.CharField(max_length=50, primary_key=True)
    lab_id = models.ForeignKey(Laboratories, on_delete=models.PROTECT)
    instrument_id = models.ForeignKey(Instruments, on_delete=models.PROTECT)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'lab_x_instrument'.lower()

class Steps(models.Model):
    widgets = {}
    step_id = models.CharField(max_length=50, primary_key=True)
    sample_id = models.ForeignKey(Samples, on_delete=models.PROTECT)
    instrument_id = models.ForeignKey(Instruments, on_delete=models.PROTECT)
    technique_id = models.ForeignKey(Techniques, on_delete=models.PROTECT)
    assigned_uoa = models.IntegerField()
    performed_uoa = models.IntegerField(default = 0)
    eff_sample_date_of_delivery = models.DateField()
    eff_reagents_date_of_delivery = models.DateField()
    steps_choices = choices["Steps"]
    sample_quality_choices = tupleConvert(steps_choices["sample_quality_choices"])
    sample_quality = models.CharField(blank=True)
    widgets["sample_quality"] = MultiChoicheAndOtherWidget(choices=sample_quality_choices)
    sample_quality_description = models.TextField(max_length=500, blank=True)
    sample_quality_extra_budjet = models.BooleanField(blank=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'steps'.lower()


class Questions(models.Model):
    question_id = models.CharField(max_length=50, primary_key=True)
    sample_id = models.ForeignKey(Samples, on_delete=models.PROTECT)
    question = models.TextField(max_length=500, blank=True)
    answer = models.TextField(max_length=500, blank=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'questions'.lower()


class Administration(models.Model):
    sr_id = models.CharField(max_length=50, primary_key=True) #  FIXME: default=uuid4() implement in forms
    lab_id = models.CharField(max_length=50)
    dmptitle = models.CharField(max_length=128, blank=True)
    user_id = models.CharField(max_length=50)
    email = models.CharField(max_length=128, blank=True)
    affiliation = models.CharField(max_length=128, blank=True)
    experimentabstract = models.TextField(max_length=500, blank=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'administration'.lower()

'''class lageSample(models.Model):
    widgets = {}

    sr_id = models.CharField(max_length=50, primary_key=True, default=uuid4())
    user_id = models.CharField(max_length=50)
    sample_description = models.TextField(max_length=500)
    
    type_of_sample_choices = (
        ("DNA","DNA"),
        ("RNA","RNA"),
        ("pellet","pellet"),
        ("biopsy","biopsy"),
    )
    type_of_sample = models.CharField(blank=True)
    widgets["type_of_sample"] = MultiChoicheAndOtherWidget(choices=type_of_sample_choices)
    
    instrument = models.ForeignKey(Instruments, blank=True, on_delete=models.CASCADE, null=True)

    is_volume_in_uL = models.CharField(blank=True)
    widgets["is_volume_in_uL"] = BooleanIfWhat(yes_or_no=False)

    is_buffer_used = models.CharField(blank=True)
    widgets["is_buffer_used"] = BooleanIfWhat(yes_or_no=False)

    expected_date_of_delivery = models.DateField(blank=False)
    
    is_quality = models.CharField(blank=True)
    widgets["is_quality"] = BooleanIfWhat(yes_or_no=False)

    sample_back = models.BooleanField(blank=True)

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'uploads/zz_old/{0}/{1}/{2}'.format(instance.user_id, instance.sr_id, filename)

    samplesheet_file = models.FileField(blank=True, upload_to=user_directory_path)

    additional_files = models.FileField(blank=True, upload_to=user_directory_path)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'lagesample'.lower()
'''

class labDMP(models.Model):
    lab_id = models.CharField(max_length=128, primary_key=True)
    user_id = models.CharField(max_length=50)
    
    # 'A) Do you collect all the metadata produced by your instruments?',3)
    instrument_metadata_collection =  models.CharField(max_length=128,blank=True)

    # 'B) Do you collect additional metadata by an open source laboratory notebook?',3)
    additional_enotebook_open_collection = models.CharField(max_length=128,blank=True)
    # 'C) Do you use a well defined standard to name your samples?',3)
    sample_standard = models.CharField(max_length=128,blank=True)
    # 'D) Do you use a well defined metadata schema and format?',3)
    metadata_schema_defined = models.CharField(blank=True) # TODO: IF YES WHICH ONE (do the widget)
    # 'III Publication phase',1)
    # 'All the answers below have to be understood in the PRP project context, that is the implementations required by the project are developing the scenario described below.')
    # '1. Data and metadata publication',2)
    # 'A) Will data and related metadata be published on an open and trusted repository with a d.o.i.?',3)
    open_trusted_repo_published_data = models.BooleanField(blank=True)
    # 'B) Will published processed data and related metadata be licensed?',3)
    open_data_licence = models.CharField(blank=True)

    # '2. Scientific publications',2)
    # 'A) Will any scientific publication arising from data and related metadata be published on an open access peer review journal or uploaded on an open access repository?',3)
    open_access_journal_publication = models.BooleanField(blank=True)

    # B) Will any scientific publication have a clear data provenance?',3)
    clear_data_provenance = models.BooleanField(blank=True)

    # 'C) Will any scientific output related to data such as presentation or posters be open access registered with a d.o.i.?',3)
    related_data_open = models.BooleanField(blank=True)

    # 'D) Will scientific publication or any other scientific document (presentation, poster, etc.) be licensed?',3)
    licence_scientific_documents = models.BooleanField(blank=True)

    # 'IV Data and Metadata storage and preservation',1)
    # '1. Storage',2)
    # 'A) Where will raw data  be stored ?',3)
    raw_data_storage_location = models.CharField(blank=True)

    # 'B) How long will raw data be preserved ?',3)
    raw_data_storage_time_retention = models.CharField(blank=True)


    # '2. Backups',2)
    # 'A) Which backup policy will be applied to published data or raw data related to published data?',3)
    backup_policy_published_data = models.CharField(blank=True)

    # 'B) Which backup policy will be applied to not published data or raw data not related to published data?',3)
    backup_policy_unplublished_data = models.CharField(blank=True)

    class Meta:
        db_table= 'labdmp'.lower()

class Results(models.Model):
    result_id = models.CharField(max_length=50, primary_key=True)
    main_repository = models.CharField(max_length=2048, blank=True)
    article_doi = models.CharField(max_length=256, blank=True)
    
    # TODO: complete the model
    class Meta:
        db_table= 'results'.lower()

class ResultxInstrument(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    results = models.ForeignKey(Results, on_delete=models.PROTECT)
    instruments = models.ForeignKey(Instruments, on_delete=models.PROTECT)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'result_x_instrument'.lower()

class ResultxSample(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    results = models.ForeignKey(Results, on_delete=models.PROTECT)
    samples = models.ForeignKey(Samples, on_delete=models.PROTECT)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'result_x_sample'.lower()

class ResultxLab(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    results = models.ForeignKey(Results, on_delete=models.PROTECT)
    lab = models.ForeignKey(Laboratories, on_delete=models.PROTECT)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'result_x_lab'.lower()
