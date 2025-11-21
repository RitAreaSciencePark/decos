from django.db import models
from django.apps import apps
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

class Struct_Bio_LabSamples(Samples):
    widgets = {}
    struct_bio_lab_choices = choices["Struct_Bio_Lab"]
    struct_bio_lab_choices["pure_or_mixture"] = [["pure", "Pure"], ["mixture", "Mixture"]]

    type_choices = tupleConvert(struct_bio_lab_choices["type_choices"])
    type = models.CharField(max_length=255, blank=True, choices=type_choices)

    # Adherent or Suspended
    adherent_or_suspended_choices = tupleConvert(struct_bio_lab_choices["adherent_or_suspended"])
    adherent_or_suspended = models.CharField(max_length=64, blank=True, choices=adherent_or_suspended_choices)
    
    # Affiliation
    affiliation = models.CharField(max_length=512, blank=True)

    # antibiotic resistance
    antibiotic_resistance = models.CharField(max_length=512, blank=True)

    # Bio Safety Level
    bio_safety_choices = tupleConvert(struct_bio_lab_choices["bio_safety"])
    bio_safety_level = models.CharField(max_length=1, blank=True, choices=bio_safety_choices)

    # Buffer Medium
    buffer_medium = models.CharField(max_length=512, blank=True)

    #cas number
    cas_number = models.CharField(max_length=256, blank=True)

    # Biological or Chemical Hazard
    chemical_hazard = models.CharField(max_length=256, blank=True)

    # Chemical Name
    chemical_name = models.CharField(max_length=256, blank=True)

    # Chemical Name CAS List
    chemical_name_CAS_list = models.TextField(blank=True)

    # Culture Medium
    culture_medium = models.CharField(max_length=256, blank=True)

    # Embedding Medium
    embedding_medium = models.CharField(max_length=256, blank=True)

    #GeneBank ID
    genebank_id = models.CharField(max_length=256, blank=True)

    molar_weight = models.CharField(max_length=256, blank=True)

    # Mycoplasma test
    mycoplasma_test =  tupleConvert(struct_bio_lab_choices["mycoplasma_test"])
    mycoplasma_test = models.CharField(max_length=3, blank=True, choices=mycoplasma_test)

    # Name
    name = models.CharField(max_length=256, blank=True)

    quality_control = models.CharField(max_length=256, blank=True)

    quantity_concentration_medium = models.CharField(max_length=256, blank=True)

    # Sample Producer
    sample_producer = models.CharField(max_length=512, blank=True)

    # Sample Purpose
    sample_purpose = models.CharField(max_length=512, blank=True)

    # Sample destination
    sample_destination_upon_usage = models.CharField(max_length=512, blank=True)

    # Sequence
    sequence = models.CharField(max_length=256, blank=True)

    # Stiffness and Roughness Ranges
    stiffness_and_roughness_ranges = models.CharField(max_length=256, blank=True)

    # Slice Thickness
    slice_thickness = models.CharField(max_length=32, blank=True)

    # Storage Conditions
    storage_choices = tupleConvert(struct_bio_lab_choices["storage"])
    storage = models.CharField(max_length=10, blank=True, choices=storage_choices)

    # Transformed with vector
    transformed_with_vector = models.CharField(blank=True)
    widgets["transformed_with_vector"] = BooleanIfWhat(yes_or_no=True) 

    # Film Thickness
    film_thickness = models.CharField(max_length=32, blank=True)

    # Is Fixed
    is_fixed = models.CharField(blank=True)
    widgets["is_fixed"] = BooleanIfWhat(yes_or_no=True)

    recombinant = models.CharField(blank=True)
    widgets["recombinant"] = BooleanIfWhat(yes_or_no=True)
    recombinant_source=models.CharField(max_length=32, blank=True)

    # Origin
    origin = models.CharField(max_length=256, blank=True)

    # Other
    other = models.TextField(blank=True)

    # Polishing
    polishing = models.CharField(blank=True)
    widgets["polishing"] = BooleanIfWhat(yes_or_no=True)

    # Pure or Mixture
    pure_or_mixture_choices = tupleConvert(struct_bio_lab_choices["pure_or_mixture"])
    pure_or_mixture = models.CharField(max_length=64, blank=True, choices=pure_or_mixture_choices)


    # Support
    support = models.CharField(max_length=256, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"Sample ({self.get_sample_type_display()})"
    
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        if(instance.sr_id):
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.sr_id.sr_id, instance.sample_id, filename)
        else:
            return 'uploads/samples/{0}/{1}/{2}'.format(instance.lab_id, instance.sample_id, filename)

    sample_sheet_filename = models.FileField(blank=True, upload_to=user_directory_path)
    additional_filename = models.FileField(blank=True, upload_to=user_directory_path)
    sequence_file = models.FileField(upload_to=user_directory_path, blank = True, null=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'struct_bio_lab_samples'.lower()
        app_label = 'PRP_CDM_app'

class Struct_Bio_LabMetadata(models.Model):
    metadata_id = models.CharField(max_length=64, unique=True)
    sample = models.ForeignKey('PRP_CDM_app.Samples', on_delete=models.CASCADE, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    formatted_voltage = models.CharField(max_length=50, blank=True, null=True)
    exposure_s = models.FloatField(blank=True, null=True)
    acquisition_date = models.DateField(blank=True, null=True)