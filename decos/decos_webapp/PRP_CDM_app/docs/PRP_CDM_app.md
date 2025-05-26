# PRP_CDM_app - Common Data Model & Ontology Manager

## Overview

The **PRP_CDM_app** serves as the **core ontology and Common Data Model (CDM)** for the **DECOS Webapp**, managing structured metadata for multicentric life sciences laboratories. It defines the **data relationships, business logic, and controlled vocabularies** that ensure consistency across laboratory systems.

This application is directly linked to the **`decos_metadata_db`** relational database and acts as the **backend and metadata catalog for the Home App**, providing **standardized storage, retrieval, and interoperability** for research data.

## Key Responsibilities

- **Common Data Model (CDM) Implementation**
  - Defines **standardized entities** for users, laboratories, instruments, and research outputs.
  - Establishes **semantic relationships** to ensure data integrity.

- **Ontology-Driven Metadata Management**
  - Provides **structured vocabularies** and **controlled terms** for experimental data.
  - Supports **cross-laboratory interoperability**.

- **Role-Based Access Control (RBAC)**
  - Laboratories are **linked to Django Groups**, ensuring **secure access** to metadata.

- **Integration with `decos_metadata_db`**
  - Manages the **core database structure** for the DECOS Webapp.
  - Ensures efficient **querying and metadata retrieval**. The decos_metadata_db is a standalone database containing only the metadata catalog.

- **Back-End for the Home App**
  - Supplies structured metadata for visualization and **searchable catalogs**.
  - Supports metadata-driven user interfaces, creating personalized form definition from the main ontology.

## Model Structure

The **Common Data Model (CDM)** serves as the foundation for laboratory data management.

### **Core Data Models**
| **Model**        | **Description** |
|-----------------|----------------|
| `Users`         | Researcher metadata, linked to Django authentication. |
| `Laboratories`  | Defines laboratories and enforces group-based access control. |
| `Proposals`     | Tracks submitted research proposals. |
| `ServiceRequests` | Manages laboratory service requests. |
| `Samples`       | Captures sample metadata, extended by lab-specific models. |
| `Instruments`   | Represents scientific instruments used in research. |
| `Techniques`    | Standardized techniques applied to samples. |
| `Results`       | Research outputs linked to metadata, publications, and experiments. |
| `LabDMP`        | Defines laboratory data management policies (FAIR compliance). |

### **Integration with Laboratory-Specific Models**
The **CDM provides a standardized base**, extended by **laboratory-specific models**:
- `PRP_CDM_app.models.laboratory_models.lage` (LAGE Laboratory)
- `PRP_CDM_app.models.laboratory_models.lame` (LAME Laboratory)

These models inherit from **core CDM structures** while defining **domain-specific attributes**.

## Form Structures & Metadata Collection

Defined in **`forms.py`**, the **metadata collection pipeline** is designed to:
- **Decouple form structures from database schemas**, enabling flexible UI design.
- **Support lab-specific metadata entry**, ensuring alignment with controlled vocabularies.

### Examples:
| **Form Name** | **Lab** | **Associated Model** | **Excluded Fields** |
|--------------|--------|-----------------|-----------------|
| `LageForm`  | LAGE   | `LageSamples`  | `sr_id`, `sample_id`, `lab_id`, `sample_feasibility`, `sample_status`, `sample_location` |
| `LameForm`  | LAME   | `LameSamples`  | `sr_id`, `sample_id`, `sample_feasibility`, `sample_status`, `sample_location` |

## Custom Fields & Metadata Standardization

Defined in **`fields.py`**, these **custom fields** enhance **metadata entry and validation** linked to custom jquery widgets in templates.

| **Field Name**              | **Description** |
|-----------------------------|----------------|
| `MultiChoicheAndOtherWidget` | Dropdown selection with optional free-text input. |
| `BooleanIfWhat`             | Checkbox with reasoning fields for selected choices. |
| **Security Enhancements**   | Input sanitization and template whitelisting. |

## Automated Identifier Generation

Defined in **`code_generation.py`**, this module ensures **structured metadata integrity** across the system.

- **Generates unique, progressive IDs** for:
  - `Proposals`
  - `Service Requests`
  - `Samples`
  - `Instruments`
  - `Results`
  and crosstable ids.
- **Maintains referential integrity** in the DECOS metadata catalog.

## Integration with the DECOS Webapp

As the **ontology and metadata backbone**, PRP_CDM_app integrates with:
- **`decos_metadata_db`**: The **core relational database** for storing structured metadata.
- **Home App**: Provides **searchable, structured catalogs** for user interfaces.
- **Laboratory-Specific Models**: Extends **CDM structures** with lab-specific attributes.
- **Role-Based Security**: Ensures **controlled access** via Django **Groups & Permissions**.

## License

This module is part of the **DECOS system** and is licensed under the **MIT License**. See the `LICENSE` file in the project root for details.

## Authors

Developed by **Marco Prenassi** and **Cecilia Zagni**,  
Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy.
