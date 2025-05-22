from django.db import models
from django.apps import apps
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

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
        app_label = 'PRP_CDM_app'
