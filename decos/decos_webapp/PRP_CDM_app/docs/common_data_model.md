# PRP_CDM_app - Common Data Model (CDM) Documentation

## Overview

The **Common Data Model (CDM)** is the **core ontology** of the **Digital ECOSystem (DECOS) of PRP@CERIC**. It provides a **standardized data structure** to ensure **semantic consistency** across multicentric life sciences laboratories. 

This model **integrates research data, service requests, laboratory infrastructure, and user roles** while ensuring interoperability between multiple laboratory systems. The CDM serves as the **foundation** for laboratory-specific extensions and domain-specific data structures.

## Key Features

- **Ontology-Driven Design**: Defines a structured and extensible framework for laboratory data representation.
- **Standardized Laboratory Data Management**: Integrates laboratories, researchers, instruments, experiments, and results.
- **Role-Based Access Control (RBAC)**: Ensures controlled access by linking Django **Groups** to **Laboratories**.
- **Interoperability & FAIR Principles**: Enables **metadata standardization** and **semantic linking** of research outputs.

## Model Relationships

The CDM **directly integrates with laboratory-specific models** under:
- `django/decos_webapp/PRP_CDM_app/models/laboratory_models/`
  - **Examples**: `lage.py`, `lame.py` (represent different laboratories)
- `django/decos_webapp/PRP_CDM_app/models/common_data_model.py` (centralized ontology)

### **High-Level Schema**

| **Entity**          | **Description** | **Key Relations** |
|---------------------|----------------|-------------------|
| **Users**          | Researcher information, linked to Django authentication. | Service Requests, Proposals |
| **Laboratories**   | Defines registered laboratories. | Service Requests, Samples, Instruments, Researchers |
| **Proposals**      | Research proposals submitted by users. | Users, Service Requests |
| **ServiceRequests** | Research service requests linked to laboratories. | Laboratories, Samples, Proposals |
| **Samples**        | Metadata on collected or analyzed samples. | Laboratories, Service Requests, Results |
| **Instruments**    | Scientific instruments used in experiments. | Laboratories, Techniques, Results |
| **Techniques**     | Scientific techniques applied in experiments. | Instruments, Results |
| **Results**        | Research outcomes, linked to metadata and publications. | Samples, Instruments, Laboratories |
| **LabDMP**         | Data Management Plan (DMP) for laboratory data policies. | Laboratories |

## Model Descriptions

### **Users**
Represents **researchers** within the **multicentric laboratory ecosystem**. Extends user authentication data with research-specific metadata.

- **Fields**: `user_id`, `name_surname`, `email`, `affiliation`, `gender`, `legal_status`, `research_role`
- **Key Relations**:
  - Linked to `Proposals`
  - Associated with **Service Requests**

### **Laboratories**
Defines **registered laboratories** in the system, each uniquely identified and linked to:
- Research proposals
- Service requests
- Samples and instruments
- User roles (Django Groups)

- **Fields**: `lab_id`, `description`
- **Key Relations**:
  - Linked to `Samples`, `Instruments`, `ServiceRequests`
  - Tied to **Django Groups** for **role-based access control**

### **Proposals**
Captures **research proposals** submitted by external users.

- **Fields**: `proposal_id`, `user_id`, `proposal_status`, `proposal_date`, `proposal_feasibility`
- **Key Relations**:
  - Linked to **Users** (`user_id`)
  - Associated with **Service Requests** (`proposal_id`)

### **ServiceRequests**
Records **requests for services** within laboratories. Can be linked to **external proposals** or **internal requests**.

- **Fields**: `sr_id`, `proposal_id`, `lab_id`, `sr_status`, `exp_description`, `output_delivery_date`
- **Key Relations**:
  - Linked to `Proposals`
  - Connected to `Laboratories`

### **Samples**
Describes **collected or analyzed biological/chemical samples**.

- **Fields**: `sample_id`, `sr_id`, `lab_id`, `sample_short_description`, `sample_description`, `sample_status`
- **Key Relations**:
  - Linked to `ServiceRequests`
  - Associated with **Results**
  - Extended by **laboratory-specific models** (e.g., `lage.py`, `lame.py`)

### **Instruments**
Stores metadata on **scientific instruments** used in experiments.

- **Fields**: `instrument_id`, `vendor`, `model`, `description`
- **Key Relations**:
  - Linked to `Techniques`
  - Used in **Results**
  - Associated with `Laboratories`

### **Techniques**
Defines **scientific techniques** applied in experiments.

- **Fields**: `technique_id`, `technique_name`, `description`
- **Key Relations**:
  - Linked to `Instruments`
  - Used in **Results**

### **Results**
Captures **research outcomes**, including dataset locations and references.

- **Fields**: `result_id`, `main_repository`, `article_doi`
- **Key Relations**:
  - Linked to **Samples**
  - Associated with `Instruments`
  - Connected to **Laboratories**

### **LabDMP (Laboratory Data Management Plan)**
Defines **FAIR data management policies** for laboratory research.

- **Fields**: Metadata policies, storage details, licensing, access policies.
- **Key Relations**:
  - Linked to **Laboratories**

## Laboratory-Specific Extensions

Laboratories may have **custom metadata models** extending the CDM:
- **Example Laboratory Models**:
  - `lage.py` (Laboratory A)
  - `lame.py` (Laboratory B)

These models **inherit from CDM structures** and define **domain-specific attributes**.

## Integration with DECOS

The **Common Data Model (CDM)** ensures:
- **Interoperability** across laboratories by enforcing a **standard ontology**.
- **Semantic linking** between **samples, experiments, instruments, and results**.
- **Role-based security** by integrating Django authentication with **laboratory permissions**.

## License

This module is part of the **DECOS system** and is licensed under the **MIT License**. See the `LICENSE` file in the project root for details.

## Authors

Developed by **Marco Prenassi** and **Cecilia Zagni**,  
Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy.
