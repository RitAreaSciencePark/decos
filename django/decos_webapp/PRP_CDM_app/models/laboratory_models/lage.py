from django.db import models
from django.apps import apps
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

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
        app_label = 'PRP_CDM_app'
