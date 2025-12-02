from django.db import models
from django.apps import apps
from PRP_CDM_app.utility import choices, tupleConvert
from PRP_CDM_app.fields import MultiChoicheAndOtherWidget, BooleanIfWhat
from PRP_CDM_app.models.common_data_model import Samples

class Nanoinnovation_LaboratorySamples(Samples):
    widgets = {}
    nanoinnovation_laboratory_choices = choices["Nanoinnovation_Laboratory"]
    nanoinnovation_laboratory_choices["pure_or_mixture"] = [["pure", "Pure"], ["mixture", "Mixture"]]

    # Sample type
    type_choices = tupleConvert(nanoinnovation_laboratory_choices["type_choices"])
    type = models.CharField(max_length=64, blank=True, choices=type_choices)

    # Adherent or Suspended
    adherent_or_suspended_choices = tupleConvert(nanoinnovation_laboratory_choices["adherent_or_suspended"])
    adherent_or_suspended = models.CharField(max_length=64, blank=True, choices=adherent_or_suspended_choices)

    # Bio Safety Level
    bio_safety_choices = tupleConvert(nanoinnovation_laboratory_choices["bio_safety"])
    bio_safety_level = models.CharField(max_length=1, blank=True, choices=bio_safety_choices)

    # Buffer Medium
    buffer_medium = models.CharField(max_length=512, blank=True)

    # Chemical Hazard
    chemical_hazard_choices = tupleConvert(nanoinnovation_laboratory_choices["chemical_hazard"])
    chemical_hazard = models.CharField(max_length=64, blank=True, choices=chemical_hazard_choices)

    # Chemical Name
    chemical_name = models.CharField(max_length=256, blank=True)

    # Chemical Name CAS List
    chemical_name_CAS_list = models.TextField(blank=True)

    # Culture Medium
    culture_medium = models.CharField(max_length=256, blank=True)

    # Embedding Medium
    embedding_medium = models.CharField(max_length=256, blank=True)

    # Stiffness and Roughness Ranges
    stiffness_and_roughness_ranges = models.CharField(max_length=256, blank=True)

    # Slice Thickness
    slice_thickness = models.CharField(max_length=32, blank=True)

    # Film Thickness
    film_thickness = models.CharField(max_length=32, blank=True)

    # Form
    powder_form_choices = tupleConvert(nanoinnovation_laboratory_choices["powder_form"])
    form = models.CharField(max_length=64, blank=True, choices=powder_form_choices)

    # Is Fixed
    is_fixed = models.CharField(blank=True)
    widgets["is_fixed"] = BooleanIfWhat(yes_or_no=True)

    # Origin
    origin = models.CharField(max_length=256, blank=True)

    # Other
    other = models.TextField(blank=True)

    # Polishing
    polishing = models.CharField(blank=True)
    widgets["polishing"] = BooleanIfWhat(yes_or_no=True)

    # Pure or Mixture
    pure_or_mixture_choices = tupleConvert(nanoinnovation_laboratory_choices["pure_or_mixture"])
    pure_or_mixture = models.CharField(max_length=64, blank=True, choices=pure_or_mixture_choices)

    # Self-standing or Free-standing
    slice_standing_choices = tupleConvert(nanoinnovation_laboratory_choices["slice_standing"])
    self_standing_or_free_standing = models.CharField(max_length=64, blank=True, choices=slice_standing_choices)

    # Support
    support = models.CharField(max_length=256, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True)

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
        db_table= 'nanoinnovation_laboratory_samples'.lower()
        app_label = 'PRP_CDM_app'
