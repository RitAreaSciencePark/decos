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
from PRP_CDM_app.models.laboratory_models.lame import LameSamples  # Import LAME-specific sample model
from PRP_CDM_app.models.laboratory_models.bio_open_lab_unisalento import Bio_Open_Lab_Unisalento  # Import LAME-specific sample model


class FormsDefinition:
    # Defines form structures for different laboratories, specifying included models and excluded fields

    class LageForm:
        # Form definition for LAGE samples
        lab = 'LAGE'
        content = [LageSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to avoid unnecessary or internal data
        exclude = { 'LageSamples': ['sr_id',
                                    'sample_id',
                                    'lab_id',
                                    'sample_feasibility',
                                    'sample_status',
                                    'sample_location']
                   }
        
    class LameForm:
        # Form definition for LAME samples
        lab = 'LAME'
        content = [LameSamples]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'LameSamples': ['sr_id',
                                    'sample_id',
                                    'sample_feasibility',
                                    'sample_status',  
                                    'sample_location']
                   }
        
    class BIO_OPEN_LAB_UNISALENTOForm:
                # Form definition for LAME samples
        lab = 'BIO OPEN LAB - UNISALENTO'
        content = [Bio_Open_Lab_Unisalento]  # Defines the model used in the form

        # Fields to be excluded from the form to ensure only relevant data is collected
        exclude = { 'Bio_Open_Lab_Unisalento': ['sr_id',
                                    'sample_id',
                                    'sample_feasibility',
                                    'sample_status',  
                                    'sample_location']
                   }
