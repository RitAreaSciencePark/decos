from django.db import models
from django.apps import apps
from django.utils import timezone
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

class Functional_Screening_FacilitySamples(Samples):
    widgets = {}
    functional_screening_facility_choices = choices["Functional_Screening_Facility"]
    type_choices = tupleConvert(functional_screening_facility_choices["type_choices"])
    type = models.CharField(max_length=255, blank=True)
    widgets["type"] = MultiChoicheAndOtherWidget(choices=type_choices)
    submitted_at = models.DateTimeField(default=timezone.now)

    # Bio Safety Level
    bio_safety_choices = tupleConvert(functional_screening_facility_choices["bio_safety"])
    bio_safety_level = models.CharField(max_length=1, blank=True, choices=bio_safety_choices)

    # Buffer Medium
    buffer_medium = models.CharField(max_length=512, blank=True)

    #Concentration
    concentration = models.CharField(max_length=255, blank=True)

    # Other
    other = models.TextField(blank=True)

    #Sample Producer
    sample_producer = models.CharField(max_length=255, blank=True)

    #Volume    
    volume = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Sample ({self.get_sample_type_display()})"
    
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        if(instance.proposal_id):
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.proposal_id, instance.sample_id, filename)
        else:
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.lab_id, instance.sample_id, filename)

    sample_sheet_filename = models.FileField(blank=True, upload_to=user_directory_path)
    additional_filename = models.FileField(blank=True, upload_to=user_directory_path)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'functional_screening_facility_samples'.lower()
        app_label = 'PRP_CDM_app'
