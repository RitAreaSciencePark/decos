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
        if(instance.proposal_id):
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.proposal_id.proposal_id, instance.sample_id, filename)
        else:
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.lab_id, instance.sample_id, filename)

    additional_filename = models.FileField(blank=True, upload_to=user_directory_path)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'bioopenlabunisalento_samples'.lower()
        app_label = 'PRP_CDM_app'

class Bio_Open_Lab_UnisalentoMetadata(models.Model):
    metadata_id = models.CharField(max_length=64, unique=True)
    sample = models.ForeignKey('PRP_CDM_app.Samples', on_delete=models.CASCADE, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    formatted_voltage = models.CharField(max_length=50, blank=True, null=True)
    exposure_s = models.FloatField(blank=True, null=True)
    acquisition_date = models.DateField(blank=True, null=True)
    acquisition_time = models.FloatField(blank=True, null=True)
    formatted_indicated_mag = models.CharField(max_length=50, blank=True, null=True)
    pixel_size_um = models.JSONField(blank=True, null=True)
    pixel_depth = models.IntegerField(blank=True, null=True)
    stage_alpha = models.CharField(max_length=50, blank=True, null=True)
    stage_beta = models.CharField(max_length=50, blank=True, null=True)
    stage_x = models.CharField(max_length=50, blank=True, null=True)
    stage_y = models.CharField(max_length=50, blank=True, null=True)
    stage_z = models.CharField(max_length=50, blank=True, null=True)
    active_size_pixels = models.JSONField(blank=True, null=True)

    class Meta:
        db_table= 'bio_open_lab_unisalentometadata'.lower()
        app_label = 'PRP_CDM_app'

    @classmethod
    def from_minio_metadata(cls, metadata_obj, sample=None):
        # Convert "N/A" strings to None and handle date conversion
        def clean(value):
            return None if value in ("N/A", "", None) else value

        # Create a new instance or update an existing one as needed
        instance = cls(
            metadata_id=clean(metadata_obj.get("metadata_id")),
            device_name=clean(metadata_obj.get("device_name")),
            formatted_voltage=clean(metadata_obj.get("formatted_voltage")),
            exposure_s=clean(metadata_obj.get("exposure_s")),
            acquisition_date=clean(metadata_obj.get("acquisition_date")),
            acquisition_time=clean(metadata_obj.get("acquisition_time")),
            formatted_indicated_mag=clean(metadata_obj.get("formatted_indicated_mag")),
            pixel_size_um=metadata_obj.get("pixel_size_um"),
            pixel_depth=metadata_obj.get("pixel_depth"),
            stage_alpha=clean(metadata_obj.get("stage_alpha")),
            stage_beta=clean(metadata_obj.get("stage_beta")),
            stage_x=clean(metadata_obj.get("stage_x")),
            stage_y=clean(metadata_obj.get("stage_y")),
            stage_z=clean(metadata_obj.get("stage_z")),
            active_size_pixels=metadata_obj.get("active_size_pixels"),
            sample=sample,
        )
        instance.save()
        return instance