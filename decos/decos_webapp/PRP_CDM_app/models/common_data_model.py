# Copyright (c) 2025 Marco Prenassi, Cecilia Zagni,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi, Cecilia Zagni
# Date: 2025-02-17
# Description: DECOS Webapp - Common Data Model
# This module defines the common data model of the Digital ECOSystem (DECOS) of PRP@CERIC; a FAIR-by-Design digital ecosystem serving multiple life sciences laboratories. 
# The common data model constitutes the core of the underlying ontology, providing standardized data structures and ensuring semantic consistency across laboratory systems.
# Laboratory-specific extensions can be found in the following paths:
# - django/decos_webapp/PRP_CDM_app/models/laboratory_models/...

import datetime
import json
import os
from pathlib import Path
from uuid import uuid4

from django import forms
from django.db import models

from PRP_CDM_app.fields import BooleanIfWhat, MultiChoicheAndOtherWidget
from PRP_CDM_app.utility import choices, tupleConvert

# FIXME: IMPORTANT, REFACTOR THE SCHEMA WITH BETTER columns NAMES! (e.g. remove [..]_id_id for fk...)

# NOTE: Handling fields with multiple choices and optional free-text input:
# In cases where a CharField should allow selection from multiple choices
# but also permit free-text input as an alternative, it must be configured as follows:
#
#    test_choices = (
#        ("A", "A"),
#        ("B", "B"),
#    )
#    test = models.CharField(blank=True)
#    widgets = {"test": MultiChoicheAndOtherWidget(choices=test_choices)}
#
# This setup applies the custom MultiChoicheAndOtherWidget to the field, enabling
# the user to select from the predefined choices or provide custom input.
#
# NOTE: If a CharField should allow selection from multiple choices only,
# without the free-text alternative, it can be declared simply as:
#
#    test = models.CharField(choices=test_choices)
#
# This will restrict the input to the defined choices without free-text input.
# NOTE: Choices for model fields are loaded from 'choices.json' via 'utility.py' as the 'choices' dictionary.
# The 'tupleConvert()' function is used to convert these values into the (key, label) tuples required by Django fields.


# This model represents researcher data within the multicentric laboratory ecosystem.
# It is linked directly to the User entity in the 'decos_webapp_db' database,
# extending user information with research-specific metadata.
class Users(models.Model):
    # Primary key representing the user identifier.
    user_id = models.CharField(max_length=50, primary_key=True)

    # Full name of the researcher.
    name_surname = models.CharField(max_length=50)

    # Contact email address.
    email = models.CharField(max_length=128)

    # Institutional affiliation.
    affiliation = models.CharField(max_length=128)

    # Predefined choices dictionary for this model, sourced externally.
    userchoices = choices["Users"]

    # Gender selection based on controlled vocabulary.
    gender_choices = tupleConvert(userchoices["gender_choices"])
    gender = models.CharField(choices=gender_choices)

    # Legal status, e.g., academic, industrial; optional field.
    legal_status_choices = tupleConvert(userchoices["legal_status_choices"])
    legal_status = models.CharField(choices=legal_status_choices, blank=True, null=True)

    # Research role within the scientific environment.
    research_role_choices = tupleConvert(userchoices["research_role_choices"])
    research_role = models.CharField(choices=research_role_choices)

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'users'.lower()

# This model represents laboratories within the multicentric laboratory ecosystem.
# Each laboratory is uniquely identified and can be associated with service requests, instruments, and researchers.
class Laboratories(models.Model):
    # Primary key representing the laboratory identifier.
    lab_id = models.CharField(max_length=50, primary_key=True)

    # Short descriptive name or identifier for the laboratory.
    description = models.CharField(max_length=50)

    # String representation of the laboratory for admin and debugging purposes.
    def __str__(self):
        return self.lab_id

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'laboratories'.lower()

# This model represents research proposals submitted by external users within the laboratory ecosystem.
# It is currently a stub and will be fully implemented once the EPIRO system is ready.
class Proposals(models.Model):
    proposal_id = models.IntegerField(primary_key=True)

    title = models.CharField(max_length=255)

    status = models.CharField(max_length=50)

    submission_date = models.DateTimeField()
    # Stored as a JSON list of integers to keep it schema-light and exact.
    scheduled_instrument_ids = models.JSONField(default=list)

    # Team leader fields (expanded from nested JSON)
    team_leader_username = models.CharField(max_length=150)
    team_leader_first_name = models.CharField(max_length=150)
    team_leader_last_name = models.CharField(max_length=150)
    team_leader_email = models.EmailField()
    
    # Team members stored as JSON list
    team_members = models.JSONField(default=list)
    
    # A proposal is linked through the steps to many laboratories (in this version the steps relation are not utilized)
    labs = models.ManyToManyField('Laboratories', through='LabXProposal')


    # Defines the upload path for proposal-related files.
    def user_directory_path(instance, filename):
        return 'uploads/proposals/{0}/{1}'.format(instance.user_id.user_id, filename)

    # Optional uploaded file related to the proposal (e.g., proposal document).
    proposal_filename = models.FileField(blank=True, upload_to=user_directory_path)

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'proposals'.lower()

class LabXProposal(models.Model):
    lab_id = models.ForeignKey(Laboratories, on_delete=models.CASCADE, related_name='lab_proposal')
    instrument_id = models.ForeignKey(Proposals, on_delete=models.CASCADE, related_name='proposal_lab')

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'lab_x_proposal'.lower()

# This model represents service requests submitted to a specific laboratory within the multicentric laboratory ecosystem.
# Service requests are generally linked to research proposals from external users but can also originate internally from the laboratory itself.
class ServiceRequests(models.Model):
    # Primary key representing the service request identifier.
    sr_id = models.CharField(max_length=50, primary_key=True)

    # Reference to the related research proposal; can be null if the request is internal.
    proposal_id = models.ForeignKey(Proposals, on_delete=models.PROTECT)

    # Target laboratory that will handle the service request.
    lab_id = models.ForeignKey(Laboratories, on_delete=models.PROTECT)

    # Status of the service request (e.g., Submitted, In Progress, Completed).
    sr_status = models.CharField(default='Submitted')

    # Description of the experiment or work requested; optional field.
    exp_description = models.TextField(max_length=500, blank=True)

    # Expected delivery date for the requested output; optional field.
    output_delivery_date = models.DateField(blank=True)

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'service_requests'.lower()

# This model represents generalized sample metadata within the multicentric laboratory ecosystem.
# It serves as the base sample description, extended by laboratory-specific models (_Samples)
# defined under 'django/decos_webapp/PRP_CDM_app/models/laboratory_models' (e.g., 'lage.py', 'lame.py').
class Samples(models.Model):
    # Primary key representing the sample identifier.
    sample_id = models.CharField(max_length=50, primary_key=True)

    # Reference to the related service request; can be null in cases where the sample is internal.
    proposal = models.ForeignKey(Proposals, on_delete=models.PROTECT, null=True)

    # Reference to the laboratory responsible for the sample.
    lab_id = models.ForeignKey(Laboratories, on_delete=models.PROTECT)

    # Short description of the sample.
    sample_short_description = models.CharField(max_length=64)

    # Detailed description of the sample; optional.
    sample_description = models.TextField(max_length=500, blank=True)

    # Predefined choices dictionary for this model, sourced externally.
    samples_choices = choices["Samples"]

    # Sample feasibility evaluation (e.g., feasible, not feasible); optional field.
    sample_feasibility_choices = samples_choices["sample_feasibility_choices"]
    sample_feasibility = models.CharField(choices=sample_feasibility_choices, blank=True)

    # Status of the sample within the laboratory workflow (e.g., Submitted, Analyzed).
    sample_status = models.CharField(default='Submitted')

    # Storage location or other laboratory-specific positioning details; optional.
    sample_location = models.CharField(blank=True, null=True)

    # GDPR sensible data?
    sensible_data = models.BooleanField(blank=True)

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'samples'.lower()

# This model represents scientific instruments within the multicentric laboratory ecosystem.
# It is currently a stub and will be fully implemented once the EPIRO system is ready.
class Instruments(models.Model):
    # Primary key representing the instrument identifier.
    instrument_id = models.CharField(max_length=50, primary_key=True)

    # Optional reference to the source SQL identifier used in external systems.
    sql_id = models.IntegerField(blank=True, null=True, unique=True)

    # Contact information for the scientist responsible for the instrument.
    instrument_scientist_username = models.CharField(max_length=128, blank=True)
    instrument_scientist_first_name = models.CharField(max_length=128, blank=True)
    instrument_scientist_last_name = models.CharField(max_length=128, blank=True)
    instrument_scientist_email = models.EmailField(max_length=254, blank=True)

    # High-level instrument metadata matching the PRP@CERIC instrument registry schema.
    instrument_name = models.CharField(max_length=256)
    nano_or_lsf = models.CharField(max_length=64, blank=True)
    published = models.BooleanField(default=False)
    data_management_plan_url = models.URLField(blank=True)
    technique = models.CharField(max_length=256, blank=True)
    institution = models.CharField(max_length=256, blank=True)
    site = models.CharField(max_length=256, blank=True)
    family = models.CharField(max_length=256, blank=True)
    installation = models.CharField(max_length=256, blank=True)
    manufacturer_and_model = models.CharField(max_length=256, blank=True)

    # Detailed capability metadata (stored as free text to accommodate structured or semi-structured data).
    applications = models.TextField(blank=True)
    source = models.TextField(blank=True)
    source_energy_range = models.CharField(max_length=256, blank=True)
    detection = models.TextField(blank=True)
    detection_energy_range = models.CharField(max_length=256, blank=True)
    overall_energy_resolution = models.CharField(max_length=256, blank=True)
    overall_spatial_resolution = models.CharField(max_length=256, blank=True)
    scanning_positioning = models.CharField(max_length=256, blank=True)
    sample = models.TextField(blank=True)
    environment = models.TextField(blank=True)
    monitors = models.TextField(blank=True)
    interoperability_features = models.TextField(blank=True)
    other_capabilities = models.TextField(blank=True)
    additional_tools = models.TextField(blank=True)
    remote_or_ira = models.CharField(max_length=128, blank=True)
    remote_control = models.CharField(max_length=128, blank=True)
    raw_data_propetary_file_formats = models.CharField(max_length=256, blank=True)
    raw_data_open_file_formats = models.CharField(max_length=256, blank=True)
    average_data_for_8hrs = models.CharField(max_length=128, blank=True)
    metadata_schema = models.CharField(max_length=256, blank=True)
    labs = models.ManyToManyField('Laboratories', through='LabXInstrument')

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'instruments'.lower()

# This model represents scientific techniques within the multicentric laboratory ecosystem.
# It is currently a stub and will be fully implemented once the EPIRO system is ready.
class Techniques(models.Model):
    # Primary key representing the technique identifier.
    technique_id = models.CharField(max_length=50, primary_key=True)

    # Name of the technique (e.g., X-ray diffraction, NMR spectroscopy).
    technique_name = models.CharField(max_length=50)

    # Brief description of the technique; optional.
    description = models.CharField(max_length=50, blank=True)

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'techniques'.lower()

# This model represents the many-to-many relationship between scientific instruments and techniques.
# It links instruments to the techniques they support within the multicentric laboratory ecosystem.
class InstrumentXTechnique(models.Model):
    # Primary key representing the association identifier.
    x_id = models.CharField(max_length=50, primary_key=True)

    # Reference to the instrument involved in the technique.
    instrument_id = models.ForeignKey(Instruments, on_delete=models.CASCADE)

    # Reference to the technique supported by the instrument.
    technique_id = models.ForeignKey(Techniques, on_delete=models.CASCADE)

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'instrument_x_technique'.lower()

# This model represents the many-to-many relationship between laboratories and scientific instruments.
# It links laboratories to the instruments they own or operate within the multicentric laboratory ecosystem.
class LabXInstrument(models.Model):
    lab_id = models.ForeignKey(Laboratories, on_delete=models.CASCADE, related_name='lab_instruments')
    instrument_id = models.ForeignKey(Instruments, on_delete=models.CASCADE, related_name='instrument_labs')

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'lab_x_instrument'.lower()

# This is a stubs, EPIRO dependent, probably will be deleted in the future
class Steps(models.Model):
    widgets = {}
    step_id = models.CharField(max_length=50, primary_key=True)
    sample_id = models.ForeignKey(Samples, on_delete=models.PROTECT)
    instrument_id = models.ForeignKey(Instruments, on_delete=models.PROTECT)
    technique_id = models.ForeignKey(Techniques, on_delete=models.PROTECT)
    assigned_uoa = models.IntegerField()
    performed_uoa = models.IntegerField(default = 0)
    eff_sample_date_of_delivery = models.DateField()
    eff_reagents_date_of_delivery = models.DateField()
    steps_choices = choices["Steps"]
    sample_quality_choices = tupleConvert(steps_choices["sample_quality_choices"])
    sample_quality = models.CharField(blank=True)
    widgets["sample_quality"] = MultiChoicheAndOtherWidget(choices=sample_quality_choices)
    sample_quality_description = models.TextField(max_length=500, blank=True)
    sample_quality_extra_budjet = models.BooleanField(blank=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'steps'.lower()

# This is a stubs, EPIRO dependent, probably will be deleted in the future
class Questions(models.Model):
    question_id = models.CharField(max_length=50, primary_key=True)
    sample_id = models.ForeignKey(Samples, on_delete=models.PROTECT)
    question = models.TextField(max_length=500, blank=True)
    answer = models.TextField(max_length=500, blank=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'questions'.lower()

# This is a placeholder for administration tables
class Administration(models.Model):
    sr_id = models.CharField(max_length=50, primary_key=True) #  FIXME: default=uuid4() implement in forms
    lab_id = models.CharField(max_length=50)
    dmptitle = models.CharField(max_length=128, blank=True)
    user_id = models.CharField(max_length=50)
    email = models.CharField(max_length=128, blank=True)
    affiliation = models.CharField(max_length=128, blank=True)
    experimentabstract = models.TextField(max_length=500, blank=True)

    # give the name of the table, lowercase for postgres (I've put a "lower() to remember")
    class Meta:
        db_table= 'administration'.lower()

# This model represents the core laboratory Data Management Plan (DMP) within the multicentric laboratory ecosystem.
# It collects information on data collection, storage, publication, and preservation practices.
# TODO: use a more specific model for PRP
class labDMP(models.Model):
    # Primary key representing the laboratory identifier.
    lab_id = models.CharField(max_length=128, primary_key=True)

    # Reference to the responsible user.
    user_id = models.CharField(max_length=50)

    # Data curator of the laboratory
    data_curator = models.CharField(max_length=128)

    # Metadata collection practices from laboratory instruments; optional.
    instrument_metadata_collection = models.CharField(max_length=128, blank=True)

    # Use of additional metadata collection via an open-source electronic notebook; optional.
    additional_enotebook_open_collection = models.CharField(max_length=128, blank=True)

    # Standard naming conventions for samples; optional.
    sample_standard = models.CharField(max_length=128, blank=True)

    # Adoption of a defined metadata schema; optional.
    metadata_schema_defined = models.CharField(blank=True)

    # Backup policy for published data or raw data related to published data; optional.
    backup_policy_published_data = models.CharField(blank=True)

    # Backup policy for unpublished data or raw data unrelated to publications; optional.
    backup_policy_unplublished_data = models.CharField(blank=True)

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'labdmp'.lower()

# This model represents research results and related information within the multicentric laboratory ecosystem.
# It stores dataset locations, publication references (e.g., DOI), and links to samples, laboratories, and instruments.
class Results(models.Model):
    # Primary key representing the result identifier.
    result_id = models.CharField(max_length=50, primary_key=True)

    # URL or path to the primary data repository containing the result; optional.
    main_repository = models.CharField(max_length=2048, blank=True)

    # DOI (Digital Object Identifier) for the published article or dataset; optional.
    article_doi = models.CharField(max_length=256, blank=True)

    # Title of the publication related to the result; optional.
    publication_title = models.CharField(max_length=512, blank=True)

    # Authors of the publication; optional.
    authors = models.TextField(blank=True)

    # Name of the journal where the work was published; optional.
    journal_name = models.CharField(max_length=256, blank=True)

    # Year of publication; optional.
    publication_year = models.PositiveIntegerField(blank=True, null=True)

        # Whether data and metadata are published in an open and trusted repository; optional.
    open_trusted_repo_published_data = models.BooleanField(blank=True)

    # Licensing practices for published data; optional.
    open_data_licence = models.CharField(blank=True)

    # Whether scientific publications are published in open access venues; optional.
    open_access_journal_publication = models.BooleanField(blank=True)

    # Whether scientific publications have clear data provenance; optional.
    clear_data_provenance = models.BooleanField(blank=True)

    # Whether scientific outputs such as presentations or posters are open access; optional.
    related_data_open = models.BooleanField(blank=True)

    # Whether scientific publications and other outputs are licensed; optional.
    licence_scientific_documents = models.BooleanField(blank=True)

    # Location where raw data is stored; optional.
    raw_data_storage_location = models.CharField(blank=True)

    # Retention period for raw data; optional.
    raw_data_storage_time_retention = models.CharField(blank=True)

    # Many-to-many relationship with ExperimentDMP through ResultxExperimentDMP
    experiment_dmps = models.ManyToManyField('ExperimentDMP', through='ResultxExperimentDMP')

    lab = models.ManyToManyField('Laboratories', through='ResultxLaboratories')

    # TODO: complete the model with additional research result metadata as needed.

    class Meta:
        # Explicit table name in lowercase for PostgreSQL compatibility.
        db_table = 'results'.lower()

# This model represents the many-to-many relationship between research results and ExperimentDMP.
# It links research outputs to the experiment DMPs involved in generating the data.
class ResultxExperimentDMP(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    result = models.ForeignKey(Results, on_delete=models.CASCADE)
    experiment_dmp = models.ForeignKey('ExperimentDMP', on_delete=models.CASCADE)

    class Meta:
        db_table = 'result_x_experiment_dmp'.lower()

class ResultxLaboratories(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    result = models.ForeignKey(Results, on_delete=models.CASCADE)
    lab = models.ForeignKey('Laboratories', on_delete=models.CASCADE)

    class Meta:
        db_table = 'result_x_laboratories'.lower()

class ExperimentDMP(models.Model):
    experiment_dmp_id = models.CharField(max_length=50, primary_key=True)
    
   # Section 1: Overview
    experiment_title = models.CharField(max_length=255)
    principal_investigator = models.CharField(max_length=255)
    affiliated_institutions = models.TextField()
    project_acronym = models.CharField(max_length=100, blank=True, null=True)
    grant_number = models.CharField(max_length=100, blank=True, null=True)
    plan_creation_date = models.DateField()
    funding_programme = models.CharField(max_length=255, blank=True, null=True)
    collaborators_roles = models.TextField(blank=True, null=True)
    ethics_approvals = models.TextField(blank=True, null=True)

    # Section 4: Allocation of Resources
    roles_responsibilities = models.TextField( blank=True, null=True)
    estimated_costs = models.TextField(blank=True, null=True)
    infrastructure_support = models.TextField(blank=True, null=True)
    public_dataset = models.TextField(blank=True, null=True)

    instruments = models.ManyToManyField('Instruments', through='ExperimentDMPxInstrument')
    samples = models.ManyToManyField('Samples', through='ExperimentDMPxSample')
    lab = models.ManyToManyField('Laboratories', through='ExperimentDMPxLab')

    class Meta:
        db_table = 'experiment_dmp'.lower()

class ExperimentDMPxInstrument(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    experiment_dmp = models.ForeignKey(ExperimentDMP, on_delete=models.CASCADE)
    instruments = models.ForeignKey(Instruments, on_delete=models.CASCADE)

    class Meta:
        db_table = 'experiment_dmp_x_instrument'.lower()

class ExperimentDMPxSample(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    experiment_dmp = models.ForeignKey(ExperimentDMP, on_delete=models.CASCADE)
    samples = models.ForeignKey(Samples, on_delete=models.CASCADE)

    class Meta:
        db_table = 'experiment_dmp_x_sample'.lower()

class ExperimentDMPxLab(models.Model):
    x_id = models.CharField(max_length=50, primary_key=True)
    experiment_dmp = models.ForeignKey(ExperimentDMP, on_delete=models.CASCADE)
    lab = models.ForeignKey(Laboratories, on_delete=models.CASCADE)

    class Meta:
        db_table = 'experiment_dmp_x_lab'.lower()
