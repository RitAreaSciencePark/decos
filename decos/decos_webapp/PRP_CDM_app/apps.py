# Copyright (c) 2025 Marco Prenassi
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-25
# Description:
# PRP_CDM_app Django application configuration.
# This module defines the application settings and initializes key models upon application startup.
# The `ready()` method ensures that models are loaded only when the application is fully initialized, 
# preventing early imports that could lead to circular dependencies.

from django.apps import AppConfig

class PrpCdmAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PRP_CDM_app'

    def ready(self):
        from .models.common_data_model import (
            Users,
            Laboratories,
            labDMP,
            Samples,
            Instruments,
            Results,
            ServiceRequests,
            ResultxSample,
            ResultxInstrument,
            ResultxLab,
            Proposals,
        )

        # Import laboratory-specific models
        from .models.laboratory_models.lage import LageSamples  # LAGE laboratory models
        from .models.laboratory_models.lame import LameSamples  # LAME laboratory models
        from .models.laboratory_models.bio_open_lab_unisalento import Bio_Open_Lab_UnisalentoSamples  # LAME laboratory models


        # Add imports here for additional laboratories when implemented
        # Example:
        # from .models.laboratory_models.labx import LabXSamples  # LABX laboratory models
