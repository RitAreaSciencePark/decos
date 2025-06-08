# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description: API entry point for interfacing with the eLabFTW electronic lab notebook (ELN) service within the DECOS system, providing experiment creation and laboratory-specific customization.

import logging
from datetime import datetime

from django.forms.models import model_to_dict
from django.template.loader import render_to_string

from PRP_CDM_app.models.laboratory_models.lage import LageSamples
from APIs.decos_elabftw_API.decos_elabftw_API import ElabFTWAPI

logger = logging.getLogger(__name__)


class DecosElabAPI(ElabFTWAPI):
    # API interface extension for creating DECOS-specific experiments in eLabFTW.

    def experiment_exists(self, title):
        # Checks if an experiment with the given title already exists in eLabFTW.
        experiments = self.get_experiments()
        return next((exp for exp in experiments if exp.get('title') == title), None)

    def _new_LAGE_experiment(self, experiment_info, username) -> str | None:
        # Creates a new LAGE experiment entry in eLabFTW.
        dict_to_render = model_to_dict(LageSamples.objects.get(pk = experiment_info.pk))

        # Validate required fields
        if 'sample_id' not in dict_to_render or 'sample_short_description' not in dict_to_render:
            raise ValueError("experiment_info is missing required fields: 'sample_id' or 'sample_short_description'.")

        title = f"{dict_to_render['sample_id']}: {dict_to_render['sample_short_description']}"

        dict_to_send = {
            'title': title,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'body': render_to_string("home/elabFTW/experiment_template.html", dict_to_render),
        }

        existing_experiment = self.experiment_exists(title)
        if existing_experiment:
            exp_id = existing_experiment.get('id')
            logger.info(f"Experiment '{title}' already exists for user {username}. Redirect to: {exp_id}")
            return exp_id

        logger.info(f"Creating LAGE experiment for user {username} with title: {title}")
        response = self.create_experiment(dict_to_send)
        exp_id = response.get('id')
        if exp_id:
            logger.info(f"Experiment created. Redirect to: {exp_id}")
            return exp_id
        else:
            logger.error(f"Experiment creation failed for user {username}. No experiment ID returned.")
            return None

    def create_new_decos_experiment(self, lab, username, experiment_info):
        # Creates a new experiment in eLabFTW based on the selected laboratory.
        lab_experiment_creators = {
            'LAGE': self._new_LAGE_experiment,
        }

        if lab.lab_id in lab_experiment_creators:
            logger.info(f"Initiating experiment creation for lab {lab.lab_id} by user {username}")
            return lab_experiment_creators[lab.lab_id](experiment_info, username)
        else:
            logger.error(f"No eLabFTW template found for laboratory ID: {lab.lab_id}")
            raise Exception(f"No laboratory eLabFTW template found for lab_id '{lab.lab_id}'")
