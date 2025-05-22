# User Authentication Forms Documentation

## Overview
This module defines custom authentication forms used in the DECOS system, extending the functionality provided by `django-allauth` to integrate user registration and login processes with the `Users` model from the `PRP_CDM_app`.

## Purpose
The custom forms handle user registration and login while ensuring that each authenticated user is reflected in the `Users` table in the DECOS system. This supports tracking and associating authenticated users with laboratory data.

## Classes

### `UserRegistrationForm`
Extends: `allauth.account.forms.SignupForm`

#### Description
This form is responsible for user registration. It extends the standard `SignupForm` from `django-allauth` but does not introduce additional fields or logic. It simply calls the base `save()` method to complete the registration process.

#### Key Method
- `save(self, request)`
  - Calls the parent `save()` method to create a user.
  - Returns the newly created `User` object.

---

### `UserLoginForm`
Extends: `allauth.account.forms.LoginForm`

#### Description
This form handles user login. It extends the standard `LoginForm` and adds a check to ensure that every authenticated user is registered in the `Users` table. If the user does not exist in `Users`, a new entry is created.

#### Key Method
- `login(self, *args, **kwargs)`
  - Checks if the user exists in the `Users` table by `user_id` (the same as `username`).
  - If not found, creates a new `Users` entry with:
    - `user_id = self.user.username`
    - `email = self.user.email`
  - Calls the parent `login()` method to complete the login process.

## Dependencies
- `django-allauth`: Provides the base `SignupForm` and `LoginForm` classes.
- `PRP_CDM_app.models.Users`: Custom user data model used in the DECOS system.
- `django.core.exceptions.ObjectDoesNotExist`: Used in the original version for error handling, though it was later optimized with `filter().exists()`.

## Logging
The `UserLoginForm` includes logging when a `Users` entry is created for a new user.
- Logs the message: `Created Users entry for <username>`

## Usage
### Registration
When a user signs up using this form, the standard `allauth` user creation process is executed.

### Login
When a user logs in:
- Their presence in `Users` is verified.
- If absent, a new `Users` entry is created.
- The standard `allauth` login process continues.

## License
This module is part of the DECOS system and is licensed under the MIT License. See the `LICENSE` file in the project root for details.

## Authors
Developed by **Marco Prenassi**, Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy.

