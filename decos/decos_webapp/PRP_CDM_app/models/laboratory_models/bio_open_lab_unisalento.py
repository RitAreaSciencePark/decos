from django.db import models
from django.apps import apps
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

class  Bio_Open_Lab_UnisalentoSamples(Samples):
    widgets = {}
    bio_open_lab_unisalento_choiches = choices["Bio_Open_Lab_Unisalento"]
   # Group 1: Sample identification
    sample_name = models.CharField(max_length=255)
    sample_producer = models.CharField(max_length=255)
    affiliation = models.CharField(max_length=255)
    sample_purpose_choices = tupleConvert(bio_open_lab_unisalento_choiches["sample_purpose"])
    sample_purpose = models.CharField(blank=True)
    widgets["sample_purpose"] = MultiChoicheAndOtherWidget(choices=sample_purpose_choices)
    sample_type_choices = tupleConvert(bio_open_lab_unisalento_choiches["sample_type"])
    sample_type = models.CharField(blank=True)
    widgets["sample_type"] = MultiChoicheAndOtherWidget(choices=sample_type_choices)
    component_name = models.CharField(max_length=255)
    component_chemical_formula = models.CharField(max_length=255)
    sheet_choices = tupleConvert(bio_open_lab_unisalento_choiches["sheet"])
    sheet = models.CharField(blank=True)
    widgets["sheet"] = MultiChoicheAndOtherWidget(choices=sheet_choices)
    layer_choices = tupleConvert(bio_open_lab_unisalento_choiches["layer"])
    layer = models.CharField(blank=True)
    widgets["layer"] = MultiChoicheAndOtherWidget(choices=layer_choices)
    colloidal_solution = models.CharField(max_length=255)
    sample_expiration_date = models.DateField(blank=True, null=True)
    
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        if(instance.sr_id):
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.sr_id.sr_id, instance.sample_id, filename)
        else:
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.lab_id, instance.sample_id, filename)

    additional_filename = models.FileField(blank=True, upload_to=user_directory_path)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'bioopenlabunisalento_samples'.lower()
        app_label = 'PRP_CDM_app'
