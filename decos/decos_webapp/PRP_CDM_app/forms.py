# Copyright (c) 2025 Marco Prenassi, Cecilia Zagni,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi, Cecilia Zagni
# Date: 2025-02-17
# Description:
# This file defines Django form structures to decouple the ontology structure from the form structure, 
# allowing a single form to include multiple tables from the ontology. It facilitates the creation of 
# user-friendly forms for collecting laboratory sample data in the PRP_CDM_app, ensuring structured, 
# efficient, and standardized metadata collection within the DECOS system.

from PRP_CDM_app.models.common_data_model import *  # Import shared data models
from PRP_CDM_app.models.laboratory_models.lage import LageSamples  # Import LAGE-specific sample model
from PRP_CDM_app.models.laboratory_models.bio_open_lab_unisalento import Bio_Open_Lab_UnisalentoSamples  # Import LAME-specific sample model
from PRP_CDM_app.models.laboratory_models.nanoinnovation_laboratory import Nanoinnovation_LaboratorySamples
from PRP_CDM_app.models.laboratory_models.mass_spectroscopy_infrastructure import Mass_Spectroscopy_InfrastructureSamples
from PRP_CDM_app.models.laboratory_models.sissi_bio import Sissi_BioSamples
from PRP_CDM_app.models.laboratory_models.iuvs import IuvsSamples
from PRP_CDM_app.models.laboratory_models.struct_bio_lab import Struct_Bio_LabSamples
from PRP_CDM_app.models.laboratory_models.cnr_ic import Cnr_IcSamples
from PRP_CDM_app.models.laboratory_models.cnr_iom import Cnr_IomSamples
from PRP_CDM_app.models.laboratory_models.biosafety_facility import Biosafety_FacilitySamples
from PRP_CDM_app.models.laboratory_models.functional_screening_facility import Functional_Screening_FacilitySamples


class FormsDefinition:
    # Defines form structures for different laboratories, specifying included models and excluded fields

    class LageForm:
        # Form definition for LAGE samples
        lab = 'LAGE'
        content = [LageSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to avoid unnecessary or internal data
        exclude = { 'LageSamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
        
    class Bio_Open_Lab_UnisalentoForm:
        # Form definition for LAME samples
        lab = 'Bio Open Lab - Unisalento'
        content = [Bio_Open_Lab_UnisalentoSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Bio_Open_Lab_UnisalentoSamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }

    class Nanoinnovation_LaboratoryForm:
        # Form definition for LAME samples
        lab = 'Nanoinnovation Laboratory'
        content = [Nanoinnovation_LaboratorySamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Nanoinnovation_LaboratorySamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
        
    class Mass_Spectroscopy_InfrastructureForm:
        # Form definition for MSI samples
        lab = 'Mass Spectroscopy Infrastructure'
        content = [Mass_Spectroscopy_InfrastructureSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Mass_Spectroscopy_InfrastructureSamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
        
    class Sissi_BioForm:
        # Form definition for sissi-bio samples
        lab = 'SISSI-Bio'
        content = [Sissi_BioSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Sissi_BioSamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
    class IuvsForm:
        # Form definition for sissi-bio samples
        lab = 'IUVS'
        content = [IuvsSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'IuvsSamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
    class Struct_Bio_LabForm:
        # Form definition for sissi-bio samples
        lab = 'Structural Biology Lab'
        content = [Struct_Bio_LabSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Struct_Bio_LabSamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
    class Cnr_IcForm:
        # Form definition for sissi-bio samples
        lab = 'Cnr Ic'
        content = [Cnr_IcSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Cnr_IcSamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
        
    class Cnr_IomForm:
        # Form definition for sissi-bio samples
        lab = 'Cnr Iom'
        content = [Cnr_IomSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Cnr_IomSamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
        
    class Biosafety_FacilityForm:
        # Form definition for sissi-bio samples
        lab = 'Biosafety Facility'
        content = [Biosafety_FacilitySamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Biosafety_FacilitySamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }
        
    class Functional_Screening_FacilityForm:
        # Form definition for functional screening facility samples
        lab = 'Functional Screening Facility'
        content = [Functional_Screening_FacilitySamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Functional_Screening_FacilitySamples': ['proposal',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location',
                                    'submitted_at']
                   }