# Laboratories App - Documentation

## Overview

The **Laboratories App** is responsible for managing laboratory records and their associations with user groups in the **PRP_CDM_app**. It ensures that each laboratory is linked to a Django **Group**, enabling role-based access control within the DECOS system.   
It is only accessible through the admin interface.

## Key Responsibilities

- **Laboratory Management**
  - Create, modify, and delete laboratory records in the `Laboratories` table.
  - Maintain data consistency between registered laboratories and user groups.

- **User Group Association**
  - Automatically create a Django `Group` with the same name as the laboratory.
  - Ensure that each group has the `laboratory=True` attribute for identification.
  - Delete the corresponding `Group` when a laboratory is removed.

- **Data Integrity & Security**
  - Enforce authentication and permission controls for adding, modifying, and deleting laboratories.
  - Verify that the number of `Laboratories` entries matches the number of `Groups` marked as laboratories.
  - Provide error handling and logging for inconsistencies and unauthorized access.

## Model Dependencies

- **`Laboratories` (PRP_CDM_app.models.common_data_model)**
  - Stores registered laboratory records.
  - Serves as the authoritative source for laboratory information.

- **`Group` (django.contrib.auth.models)**
  - Represents user roles and permissions.
  - Used to enforce access control within the DECOS system.

## Views and Functionalities

| View Name          | Description |
|--------------------|-------------|
| **`AddLabView`**  | Creates a new laboratory and assigns a corresponding Django user group. Validates form data and ensures group-laboratory consistency. |
| **`ModifyLabView`** | Updates an existing laboratory record. Ensures proper authentication and handles invalid records gracefully. |
| **`DeleteLabView`** | Deletes a laboratory and its associated user group. Implements security validation and logs errors for missing records. |

## Integration with DECOS

The Laboratories App plays a fundamental role in defining **which laboratories exist** and **who belongs to them**. Other DECOS components reference these records to associate research data, experiments, and pipelines with the correct institutions.

## License

This module is part of the DECOS system and is licensed under the MIT License. See the `LICENSE` file in the project root for details.

## Author

Developed by **Marco Prenassi**, Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy.
