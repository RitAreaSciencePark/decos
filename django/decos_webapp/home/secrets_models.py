# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description:
# This file defines the API_Tokens model for the Decos Webapp - Home App.
# The model is used to store API tokens associated with a user and laboratory.
# It handles tokens for the elab and jenkins services.

from django.db import models
from django.contrib.auth.models import User

class API_Tokens(models.Model):
    # Represents the user associated with the API tokens.
    # It is recommended to use a ForeignKey to the User model for better data integrity.
    user_id = models.CharField(max_length=50)

    # Represents the laboratory associated with the API tokens.
    laboratory = models.CharField(max_length=50)

    # Token for accessing the elab service.
    # This field is optional (null and blank allowed).
    elab_token = models.CharField(max_length=128, null=True, blank=True)

    # Token for accessing the jenkins service.
    # This field is optional (null and blank allowed).
    jenkins_token = models.CharField(max_length=128, null=True, blank=True)

    # MINIO tokens for object storage access.
    # FIXME: Implement security measures for handling sensitive tokens.
    minio_acces_key = models.CharField(max_length=128, null=True, blank=True)
    minio_secret_key = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        # Specifies the name of the database table as 'api_tokens'.
        db_table= 'API_tokens'.lower()

        # Associates this model with the 'home' application.
        app_label = 'home'
