# **DECOS Webapp - README**

## **1. Project Overview**

The **DECOS Webapp** is a **Django Wagtail-based system** designed to manage structured metadata and research data across multicentric **life sciences laboratories**. It provides a **Common Data Model (CDM)** for laboratories, ensuring standardized metadata storage, controlled vocabularies, and seamless interoperability across research institutions.

This platform is developed as part of the [**PRP@CERIC**](https://www.pathogen-ri.eu/) project , aiming to establish a digitally integrated ecosystem for pathogen research. The initiative connects **academic, industrial, and public health sectors**, facilitating interdisciplinary collaboration in the study of human, animal, and plant pathogens. By integrating expertise in **biology, biochemistry, chemistry, physics, bioelectronics, omics sciences, and data science**, PRP@CERIC supports both fundamental and applied research in infectious diseases and life sciences.

The **DECOS Webapp** plays a crucial role in this initiative by providing a robust platform for **metadata management**, ensuring data is **Findable, Accessible, Interoperable, and Reusable (FAIR)**. The system enables structured data collection, standardization, and interoperability, supporting open and collaborative research.

The architecture's main component is hosted at the **ORFEO Data Center** in Trieste, which acts as the **main datalake** for managing and storing research data.

**Key Features**

- **[Django](https://www.djangoproject.com/) & [Wagtail](https://wagtail.org/) Integration**: Provides a structured metadata catalog with a flexible user interface. 
- **Ontology-Driven Metadata Management**: Ensures FAIR-compliant data collection and standardization.
- **Role-Based Access Control (RBAC)**: Links laboratories to Django Groups for secure access control.
- **API Integrations**: Seamless connections with MinIO, eLabFTW, and Jenkins for data storage and processing.
  - **[MinIO](https://min.io/)**: A high-performance object storage system compatible with Amazon S3, used for securely storing large datasets and research files. 
  - **[eLabFTW](https://www.elabftw.net/)**: An electronic laboratory notebook (ELN) for managing experiments, protocols, and scientific data in a structured way. 
  - **[Jenkins](https://www.jenkins.io/)**: A continuous integration and automation server that orchestrates data pipelines, automating workflows and processing research datasets. 
- **Modular Architecture**: Composed of three core apps:
  - **Home App**: Manages user interface and API interactions.
  - **Laboratories App**: Oversees laboratory records and access control.
  - **PRP_CDM_app**: Serves as the core ontology and metadata catalog.

## **1. Project Overview**

The **DECOS Webapp** is a **Django Wagtail-based system** designed to manage structured metadata and research data across multicentric **life sciences laboratories**. It provides a **Common Data Model (CDM)** for laboratories, ensuring standardized metadata storage, controlled vocabularies, and seamless interoperability across research institutions.

This platform is developed as part of the **PRP@CERIC** project, aiming to establish a digitally integrated ecosystem for pathogen research. The initiative connects **academic, industrial, and public health sectors**, facilitating interdisciplinary collaboration in the study of human, animal, and plant pathogens. By integrating expertise in **biology, biochemistry, chemistry, physics, bioelectronics, omics sciences, and data science**, PRP@CERIC supports both fundamental and applied research in infectious diseases and life sciences.

The **DECOS Webapp** plays a crucial role in this initiative by providing a robust platform for **metadata management**, ensuring data is **Findable, Accessible, Interoperable, and Reusable (FAIR)**. The system enables structured data collection, standardization, and interoperability, supporting open and collaborative research.

This architecture is hosted at the **ORFEO Data Center** in Trieste, which acts as the **main datalake** for managing and storing research data.

### **Key Features**
- **Django & Wagtail Integration**: Provides a structured metadata catalog with a flexible user interface.  
- **Ontology-Driven Metadata Management**: Ensures FAIR-compliant data collection and standardization.  
- **Role-Based Access Control (RBAC)**: Links laboratories to Django **Groups** for secure access control.  
- **API Integrations**: Seamless connections with **MinIO, eLabFTW, and Jenkins** for data storage and processing.  
  - **MinIO**: A high-performance **object storage system** compatible with Amazon S3, used for securely storing large datasets and research files.  
  - **eLabFTW**: An **electronic laboratory notebook (ELN)** for managing experiments, protocols, and scientific data in a structured way.  
  - **Jenkins**: A **continuous integration and automation server** that orchestrates data pipelines, automating workflows and processing research datasets.  
- **Modular Architecture**: Composed of three core apps:  
  - **Home App**: Manages user interface and API interactions.  
  - **Laboratories App**: Oversees laboratory records and access control.  
  - **PRP_CDM_app**: Serves as the core **ontology and metadata catalog**.

---

## **2. System Architecture**

The **DECOS Webapp** follows a **modular and service-oriented architecture**, ensuring flexibility, scalability, and interoperability. The platform is structured into three main Django applications, each responsible for specific functionalities within the **PRP@CERIC** ecosystem.

### **Core Components**

The system consists of the following key components:

1. **Home App (`home/`)** – Manages the **web interface** and user interactions.
2. **PRP_CDM_app (`PRP_CDM_app/`)** – Implements the **Common Data Model (CDM)** and metadata catalog.
3. **Laboratories App (`laboratories/`)** – Handles **laboratory records** and **role-based access control (RBAC)**.

Additionally, the system integrates external services for **data storage, metadata management, and automation**.

---

### **Architectural Overview**

The architecture is designed to handle **structured metadata**, enforce **FAIR principles**, and support **interoperability** among research institutions.

```
+------------------------------------------------------+
|                    DECOS Webapp                      |
|  (Django Wagtail-based metadata & research system)  |
+------------------------------------------------------+
|      Home App      |     PRP_CDM_app     |  Laboratories App  |
|   (UI & API)      |  (Ontology & CDM)   |  (Lab Management)  |
+------------------------------------------------------+
|  PostgreSQL (Relational DB)   |   MinIO (Object Storage)  |
|  Metadata & user management   |   Research data storage   |
+------------------------------------------------------+
|     External Integrations     |
|  eLabFTW  |  Jenkins  |
+------------------------------------------------------+
```

---

### **Detailed Component Breakdown**

#### **1. Home App (`home/`)**
- Acts as the **frontend** and **API gateway**.
- Implements authentication, **user interface elements**, and API request handling.
- Integrates with **eLabFTW, Jenkins, and MinIO**.
- Manages **Django Forms, Templates, and Wagtail-based pages**.

#### **2. PRP_CDM_app (`PRP_CDM_app/`)**
- Serves as the **Common Data Model (CDM) manager**.
- Defines **ontology-driven metadata models** for laboratory research.
- Manages metadata storage in **PostgreSQL**, backed by **ORFEO Data Lake**.
- Implements **controlled vocabularies and ontology-based relationships**.
- Provides structured **metadata APIs** for interoperability.

#### **3. Laboratories App (`laboratories/`)**
- Manages **laboratory records and user roles**.
- Enforces **role-based access control (RBAC)** via Django **Groups**.
- Ensures consistency between **registered labs and associated groups**.
- Accessible only through the **admin interface**.

---

### **Data Storage & Processing Infrastructure**

#### **Databases**
- **PostgreSQL (`decos_metadata_db`)**: Stores structured metadata and user roles.
- **MinIO (Object Storage)**: Handles research data files, experiment results, and raw datasets. External.

#### **External Integrations**
- **eLabFTW**: Provides an **Electronic Laboratory Notebook (ELN)** for managing experiments.
- **Jenkins**: Automates **data processing pipelines** and metadata updates.

---

## **3. Data Management**

The **PRP_CDM_app** serves as the backbone of **DECOS Webapp**, ensuring structured metadata management and interoperability across life sciences laboratories.

### **Common Data Model (CDM)**
The **Common Data Model (CDM)** defines a standardized structure for research metadata, ensuring consistency across laboratories and research projects. Key entities include:

| **Model**        | **Fields** | **Relationships** |
|-----------------|-----------|------------------|
| **Users** | user_id, name_surname, email, affiliation, userchoices, gender_choices, gender, legal_status_choices, legal_status, research_role_choices, research_role | None |
| **Laboratories** | lab_id, description | None |
| **Proposals** | proposal_id, user_id, proposal_status, proposalschoices, proposal_feasibility_choices, proposal_feasibility, proposal_date, proposal_filename | Users |
| **ServiceRequests** | sr_id, proposal_id, lab_id, sr_status, exp_description, output_delivery_date | Proposals, Laboratories |
| **Samples** | sample_id, sr_id, lab_id, sample_short_description, sample_description, samples_choices, sample_feasibility_choices, sample_feasibility, sample_status, sample_location | ServiceRequests, Laboratories |
| **Instruments** | instrument_id, vendor, model, description | None |
| **Techniques** | technique_id, technique_name, description | None |
| **Steps** | widgets, step_id, sample_id, instrument_id, technique_id, assigned_uoa, performed_uoa, eff_sample_date_of_delivery, eff_reagents_date_of_delivery, steps_choices, sample_quality_choices, sample_quality, sample_quality_description, sample_quality_extra_budget | Samples, Instruments, Techniques |
| **Questions** | question_id, sample_id, question, answer | Samples |
| **Administration** | sr_id, lab_id, dmptitle, user_id, email, affiliation, experimentabstract | None |
| **labDMP** | lab_id, user_id, instrument_metadata_collection, additional_enotebook_open_collection, sample_standard, metadata_schema_defined, open_trusted_repo_published_data, open_data_licence, open_access_journal_publication, clear_data_provenance, related_data_open, licence_scientific_documents, raw_data_storage_location, raw_data_storage_time_retention, backup_policy_published_data, backup_policy_unplublished_data | None |
| **Results** | result_id, main_repository, article_doi | None |

### **Cross Tables**
These tables represent **many-to-many relationships** within the Common Data Model:

| **Cross Table** | **Fields** | **Relationships** |
|-----------------|-----------|------------------|
| **InstrumentXTechnique** | x_id, instrument_id, technique_id | Instruments, Techniques |
| **LabXInstrument** | lab_id, instrument_id | Laboratories, Instruments |
| **ResultxInstrument** | x_id, results, instruments | Results, Instruments |
| **ResultxSample** | x_id, results, samples | Results, Samples |
| **ResultxLab** | x_id, results, lab | Results, Laboratories |

This table structure ensures the **proper linking of entities** across the metadata model, allowing for complex relationships and scalable data management.

### **Laboratory-Specific Sample Extensions**
Each laboratory may require additional metadata fields specific to their research needs. The **Common Data Model (CDM)** is extended in laboratory-specific models within the `PRP_CDM_app/models/laboratory_models/` directory to accommodate these requirements.

#### **File Structure for Laboratory-Specific Models**
The extensions to the sample model are stored in the following structured format:

```
PRP_CDM_app/
│-- models/
│   │-- common_data_model.py  # Defines the base sample model
│   │-- laboratory_models/
│   │   │-- lage.py  # Extension for LAGE laboratory
│   │   │-- lame.py  # Extension for LAME laboratory
│   │   │-- labx.py  # Additional laboratory-specific extensions
```

Each laboratory model (`lage.py`, `lame.py`, `labx.py`, etc.) inherits from the **base sample model** in `common_data_model.py`, ensuring a consistent structure while enabling **customized metadata handling** for each lab's research focus.

#### **Key Features of Laboratory Extensions**
- **Modular Inheritance**: Each lab-specific model extends the base sample model, preserving data consistency.
- **Custom Metadata Fields**: Laboratories can define additional attributes required for their workflows.
- **Scalability**: New laboratory models can be added without modifying the core **Common Data Model (CDM)**.

This structured approach ensures flexibility while maintaining **standardization and interoperability** across multiple laboratories.

---

### **Security & Access Control**

The **DECOS Webapp** implements role-based access control (RBAC) and authentication mechanisms to ensure secure data access and user management.

#### **Role-Based Access Control (RBAC)**
- **Django Groups & Permissions**: Laboratories are linked to Django **Groups**, enforcing controlled access to metadata and resources.
- **Custom Role Assignments**:
  - **Admins**: Have full access to the **Django Admin Panel**, allowing them to personalize pages, add or remove roles and laboratories, and modify system-wide elements such as headers and footers. Admins can also manage metadata and user permissions.
  - **Researchers**: Have access to their assigned laboratory data and may be granted additional roles enabling specialized functionalities, such as managing **Jenkins pipelines**.
  - **Guests**: Limited to viewing the **Home Page** and publicly available metadata, with no access to restricted system functionalities.
- **Laboratory Isolation**: Each laboratory’s data is protected, ensuring users can only access records associated with their assigned group.

#### **Authentication System**
- **[Authentik](https://goauthentik.io/) (Stub)**: The system will integrate **Authentik** for authentication in future updates.
- **Current Authentication**:
  - Uses **Django Allauth** for user registration and authentication.
  - Authentication credentials are securely stored and managed.
  - Configurable authentication settings located in `decos_webapp/settings/base.py`.

#### **Secret Management & Data Accessibility**
- All **sensitive credentials and secrets** are managed within the **Home App**, ensuring a secure separation of authentication and access-related configurations.
- The **`decos_metadata_db`** contains **no stored secrets** and can be queried or exported directly for research and reporting purposes.
- While **user-related metadata** is present in `decos_metadata_db`, future updates will introduce **improved user data management** to enhance privacy and access controls.

---

### **Project Dependencies (requirements.txt)**

The **DECOS Webapp** relies on several key dependencies for its operation. Below is a list of the main dependencies along with their respective functionalities and references to their official documentation.

#### **Core Framework and Web Server**
- **[Django](https://www.djangoproject.com/)** (>=5.0.1) - The core web framework for the application.
- **[Wagtail](https://wagtail.org/)** (>=6.0.2) - A Django-based CMS, used for managing structured content.
- **[Gunicorn](https://gunicorn.org/)** (>=21.2.0) - A production-grade WSGI HTTP server for deploying the application.

#### **Development and Debugging**
- **[debugpy](https://github.com/microsoft/debugpy)** (>=1.8.1) - Enables debugging support, allowing external tools to attach and inspect the running application.

#### **Database and ORM Support**
- **[psycopg2-binary](https://www.psycopg.org/)** (>=2.9.9) - PostgreSQL database adapter for Django, enabling efficient interaction with the database.

#### **Authentication and User Management**
- **[django-allauth](https://www.intenct.nl/projects/django-allauth/)** (>=0.62.1) - Provides authentication, registration, and account management functionalities.

#### **Data Handling and Querying**
- **[django-tables2](https://django-tables2.readthedocs.io/)** (>=2.7.0) - Facilitates table rendering, filtering, and pagination in Django views.
- **[django-filter](https://django-filter.readthedocs.io/)** (>=24.3) - Adds dynamic filtering capabilities to query data efficiently.

#### **Object Storage Integration**
- **[MinIO](https://min.io/)** (>=7.2.15) - The MinIO API, used for integrating object storage functionalities.

---

### **License**

The **DECOS Webapp** is licensed under the **MIT License**, ensuring broad usability while maintaining compliance with open-source principles. Below is an overview of the licensing structure for DECOS and its dependencies.

#### **DECOS License**
- **MIT License** - The core DECOS Webapp is distributed under the **MIT License**, permitting unrestricted use, modification, and distribution, provided the original copyright notice is included. 
- Copyright (c) 2025 **Marco Prenassi, Cecilia Zagni**, Laboratory of Data Engineering, **Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy**.

#### **Third-Party Licenses**
DECOS Webapp includes code from several third-party libraries, each under a **permissive open-source license**:

- **Django**: Three-clause **BSD License** (included in `LICENSE.django`). [Django](https://www.djangoproject.com/)
- **Python Standard Library**: **Python License** (included in `LICENSE.python`). [Python](https://docs.python.org/3/license.html)
- **Gunicorn**: **MIT License** (included in `decos/LICENSES/LICENSE.gunicorn`). [Gunicorn](https://gunicorn.org/)
- **Debugpy**: **MIT License** (included in `decos/LICENSES/LICENSE.debugpy`). [Debugpy](https://github.com/microsoft/debugpy)
- **psycopg2-binary**: **LGPL License** (included in `decos/LICENSES/LICENSE.psycopg2`). [psycopg2](https://www.psycopg.org/)
- **django-allauth**: **MIT License** (included in `decos/LICENSES/LICENSE.allauth`). [django-allauth](https://www.intenct.nl/projects/django-allauth/)
- **django-tables2**: **Simplified BSD License** (included in `decos/LICENSES/LICENSE.django-tables2`). [django-tables2](https://django-tables2.readthedocs.io/)
- **django-filter**: **MIT License** (included in `decos/LICENSES/LICENSE.django-filter`). [django-filter](https://django-filter.readthedocs.io/)
- **MinIO**: **Apache License 2.0** (included in `decos/LICENSES/LICENSE.minio`). [MinIO](https://min.io/)

---