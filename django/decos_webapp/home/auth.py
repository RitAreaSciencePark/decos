# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-17
# Description: Custom user authentication and registration forms for the DECOS system, integrating user data validation and persistence within the PRP_CDM_app ecosystem.

from allauth.account.forms import SignupForm, LoginForm
from django.decos_webapp.PRP_CDM_app.ontology.common_data_model import Users
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class UserRegistrationForm(SignupForm):
    # Custom registration form to extend the default allauth SignupForm.

    def save(self, request):
        # Perform standard signup process and return the user object.
        return super().save(request)

class UserLoginForm(LoginForm):
    # Custom login form to extend the default allauth LoginForm.

    def login(self, *args, **kwargs):
        # Check if the user has an entry in the Users table; create one if it doesn't exist.
        if not Users.objects.filter(pk=self.user.username).exists():
            user = Users(user_id=self.user.username, email=self.user.email)
            user.save()
            logger.info(f"Created Users entry for {self.user.username}")

        # Proceed with the standard login process and return the result.
        return super().login(*args, **kwargs)
