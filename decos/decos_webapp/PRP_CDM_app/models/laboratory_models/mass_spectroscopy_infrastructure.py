from django.db import models
from django.apps import apps
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

class Mass_Spectroscopy_InfrastructureSamples(Samples):
    widgets = {}
    mass_spectroscopy_infrastructure_choices = choices["Mass_Spectroscopy_Infrastructure"]
    type_choices = tupleConvert(mass_spectroscopy_infrastructure_choices["type_choices"])
    type = models.CharField(max_length=255, blank=True)
    widgets["type"] = MultiChoicheAndOtherWidget(choices=type_choices)


    #sample_id = models.CharField(max_length=50, primary_key=True) # also FK table samples
    volume_weight = models.CharField(max_length=255)
    biological_replicates = models.CharField(max_length=255)
    ##solubilized = models.BooleanField(default=False)
    solubilized = models.CharField(
        max_length=3,
        choices=[("yes", "Yes"), ("no", "No")],
        blank=True,
        null=True,
    )
    buffer_name = models.CharField(max_length=255)
    sample_date = models.DateField(blank=True, null=True)
    dry_ice = models.CharField(
        max_length=3,
        choices=[("yes", "Yes"), ("no", "No")],
        blank=True,
        null=True,
    )

    cell_counting = models.CharField(
        max_length=3,
        choices=[("yes", "Yes"), ("no", "No")],
        blank=True,
        null=True,
    )

    bradford = models.CharField(
        max_length=3,
        choices=[("yes", "Yes"), ("no", "No")],
        blank=True,
        null=True,
    )

    sample_return = models.CharField(
        max_length=3,
        choices=[("yes", "Yes"), ("no", "No")],
        blank=True,
        null=True,
    )
    results_deadline = models.DateField(blank=True, null=True)



    
    
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
        db_table= 'msi_samples'.lower()
        app_label = 'PRP_CDM_app'

class Mass_Spectroscopy_InfrastructureMetadata(models.Model):
    metadata_id = models.CharField(max_length=64, unique=True)
    sample = models.ForeignKey('PRP_CDM_app.Samples', on_delete=models.CASCADE, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    formatted_voltage = models.CharField(max_length=50, blank=True, null=True)
    exposure_s = models.FloatField(blank=True, null=True)
    acquisition_date = models.DateField(blank=True, null=True)

