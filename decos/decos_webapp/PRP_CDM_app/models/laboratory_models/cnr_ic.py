from django.db import models
from django.apps import apps
from django.utils import timezone
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

class Cnr_IcSamples(Samples):
    widgets = {}
    cnr_ic_choices = choices["Cnr_Ic"]

    type_choices = tupleConvert(cnr_ic_choices["type_choices"])
    type = models.CharField(max_length=255, blank=True, choices=type_choices)
   

    assay_temperature = models.CharField(max_length=55, blank=True)

    buffer = models.CharField(max_length=255, blank=True)
    
    concentration = models.CharField(max_length=25, blank=True)

    isoelectric_point = models.CharField(max_length=25, blank=True)

    kd_technique = models.CharField(max_length=255, blank=True)

    ligand_choices = tupleConvert(cnr_ic_choices["ligand"])
    ligand = models.CharField(max_length=255, blank=True, choices=ligand_choices)

    molecular_weight = models.CharField(max_length=55, blank=True)

    running_buffer = models.CharField(max_length=255, blank=True)

    solubility = models.CharField(max_length=55, blank=True)

    # Storage Conditions
    storage_choices = tupleConvert(cnr_ic_choices["storage"])
    storage = models.CharField(max_length=10, blank=True, choices=storage_choices)

    target_choices = tupleConvert(cnr_ic_choices["target"])
    target = models.CharField(max_length=255, blank=True, choices=target_choices)

    
    tag = models.CharField(max_length=255, blank=True)

    submitted_at = models.DateTimeField(default=timezone.now)
    


    def __str__(self):
        return f"Sample ({self.get_sample_type_display()})"

    
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        if(instance.proposal_id):
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.proposal_id.proposal_id, instance.sample_id, filename)
        else:
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.lab_id, instance.sample_id, filename)

    sample_sheet_filename = models.FileField(blank=True, upload_to=user_directory_path)
    additional_filename = models.FileField(blank=True, upload_to=user_directory_path)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'cnr_ic_samples'.lower()
        app_label = 'PRP_CDM_app'

class Cnr_IcMetadata(models.Model):
    metadata_id = models.CharField(max_length=64, unique=True)
    sample = models.ForeignKey('PRP_CDM_app.Samples', on_delete=models.CASCADE, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    formatted_voltage = models.CharField(max_length=50, blank=True, null=True)
    exposure_s = models.FloatField(blank=True, null=True)
    acquisition_date = models.DateField(blank=True, null=True)