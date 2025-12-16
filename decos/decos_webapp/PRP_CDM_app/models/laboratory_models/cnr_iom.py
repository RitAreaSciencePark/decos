from django.db import models
from django.apps import apps
from django.utils import timezone
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

class Cnr_IomSamples(Samples):
    widgets = {}
    cnr_iom_choices = choices["Cnr_Iom"]

    biological_material_description = models.CharField(max_length=255, blank=True)
    expression_methods = models.CharField(max_length=255, blank=True)

    buffering = models.CharField(max_length=255, blank=True)

    concentration = models.CharField(max_length=255, blank=True)

    grid_type = models.CharField(max_length=255, blank=True)


    molecular_weight = models.CharField(max_length=255, blank=True)

    fixation_method = models.CharField(max_length=255, blank=True)

    labelling_method_category = models.CharField(max_length=255, blank=True)
    labelling_method_dyes = models.CharField(max_length=255, blank=True)
    immunolabelling_method = models.CharField(max_length=255, blank=True)
    labelling_method_probe = models.CharField(max_length=255, blank=True)

    organization = models.CharField(max_length=85, blank=True)

    purification_stabilization = models.CharField(max_length=255, blank=True)

    purpose_choices = tupleConvert(cnr_iom_choices["purpose"])
    purpose = models.CharField(max_length=55, blank=True, choices=purpose_choices)

    sample_acronym = models.CharField(max_length=255, blank=True)
    sample_name = models.CharField(max_length=255, blank=True)

    sequence = models.CharField(max_length=255, blank=True)

    substrate_treatement = models.CharField(max_length=255, blank=True)

    submitted_at = models.DateTimeField(default=timezone.now)

    
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        if(instance.proposal_id):
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.proposal_id.proposal_id, instance.sample_id, filename)
        else:
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.lab_id, instance.sample_id, filename)

    sample_sheet_filename = models.FileField(blank=True, upload_to=user_directory_path)
    additional_filename = models.FileField(blank=True, upload_to=user_directory_path)
    sequence_file = models.FileField(upload_to=user_directory_path, blank = True, null=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'cnr_iom_samples'.lower()
        app_label = 'PRP_CDM_app'