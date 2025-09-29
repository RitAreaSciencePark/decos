# **DECOS Webapp - README**

## **1. Project Overview**

The **DECOS Webapp** is a **Django Wagtail-based system** designed for managing structured metadata and research data across multicentric **life sciences laboratories**. It provides a **Common Data Model (CDM)** to ensure standardized metadata storage, controlled vocabularies, and seamless interoperability across research institutions.

Developed as part of the [**PRP@CERIC**](https://www.pathogen-ri.eu/) project, this platform facilitates interdisciplinary collaboration between **academic, industrial, and public health sectors** for studying human, animal, and plant pathogens. The system integrates expertise from biology, biochemistry, chemistry, physics, bioelectronics, omics sciences, and data science to support fundamental and applied research in infectious diseases and life sciences.

The **DECOS Webapp** ensures that research data is **Findable, Accessible, Interoperable, and Reusable (FAIR)** by enabling structured data collection, standardization, and interoperability. It is hosted at the **ORFEO Data Center** in Trieste, which acts as the **main datalake** for managing and storing research data.

### **Key Features**
- **Django & Wagtail Integration**: A flexible metadata catalog with a user-friendly interface.
- **Ontology-Driven Metadata Management**: Ensures compliance with FAIR principles for standardized data collection.
- **Role-Based Access Control (RBAC)**: Secure user access based on laboratory affiliations and permissions.
- **API Integrations**: Seamless connections with **MinIO**, **eLabFTW**, and **Jenkins** for data storage, management, and workflow automation.
- **Modular Architecture**: Composed of three core applications:
  - **Home App**: Manages the web interface and API interactions.
  - **Laboratories App**: Handles laboratory records and access control.
  - **PRP_CDM_app**: Manages the core metadata catalog and ontology.

---

## **2. System Architecture & Component Breakdown**

The **DECOS Webapp** follows a **modular and service-oriented architecture**, ensuring flexibility, scalability, and interoperability. The system consists of the following core components:

- **Home App (`home/`)**: Manages the web interface, authentication, user interactions, and API integrations with **eLabFTW**, **MinIO**, and **Jenkins**.
- **PRP_CDM_app (`PRP_CDM_app/`)**: Manages the **Common Data Model (CDM)** and metadata catalog, ensuring structured data organization and compliance with interoperability standards.
- **Laboratories App (`laboratories/`)**: Handles **laboratory records** and **role-based access control (RBAC)** to ensure secure data management.
- **APIs (`APIs/`)**: Provides integration with external services for data storage, management, and automation.

### **Project File Structure**
The project follows a structured directory format to ensure modularity and maintainability:

```
django/├── decos_webapp/
    ├── PRP_CDM_app/
    |   ├── models/
    |   |   ├── common_data_model.py  # Core Common Data Model definitions
    |   |   ├── laboratory_models/  # Extensions for lab-specific metadata
    |   |   └── (additional models and logic for CDM)
    |   └── (metadata catalog and related logic)
    ├── laboratories/  # Manages laboratory data and role-based access control
    ├── home/  # Web interface and authentication
    ├── media/  # Static and media files
    ├── APIs/  # API integrations
    └── decos_webapp/  # Core Django project settings and configurations
```

This structure ensures that:
- **Metadata management** is centralized in `PRP_CDM_app/models/common_data_model.py`.
- **Laboratory-specific models** extend from `PRP_CDM_app/models/laboratory_models/`.
- **APIs and services** are modularly integrated.

---

## **3. Prerequisites**

Before setting up the **DECOS Webapp**, ensure you have the following installed:

1. **Docker**  
   - Install **Docker**: [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows/macOS) or [Docker on Debian](https://docs.docker.com/engine/install/debian/).
   - Verify installation:
     ```bash
     docker --version
     ```

2. **Git**  
   - Install **Git**: [Download Git](https://git-scm.com/downloads).
   - Verify installation:
     ```bash
     git --version
     ```

3. **Visual Studio Code (VS Code)**  
   - Install **VS Code**: [Download VS Code](https://code.visualstudio.com/).
   - Install the **Dev Containers** extension for remote development (optional).

4. **Docker Compose**  
   - Install Docker Compose following the [official guide](https://docs.docker.com/compose/install/). For **Windows/macOS**, Docker Compose is included in **Docker Desktop**.

---

## **4. Installation Guide**

### **Step-by-Step Installation**

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/RitAreaSciencePark/decos.git
   cd decos
   ```

2. **Run the Installation Script**  
   For a **clean setup** (wiping databases and rebuilding containers), run:
   ```bash
   sh install_clean_debug_mode.sh
   ```

3. **Start Debugging**  
   Open **VS Code**, go to **Run and Debug** (`Ctrl+Shift+D`), and select **Python Debugger: Remote Attach** to start the server. When successful, you will see:
   ```
   Starting development server at http://0.0.0.0:8080/
   Quit the server with CONTROL-C.
   ```

4. **Access the Web Application**  
   Visit the application at:
   ```
   http://decos.localhost:8080
   ```

---

## **5. Security & Access Control**

The **DECOS Webapp** implements **Role-Based Access Control (RBAC)** to ensure secure data management.

- **Django Groups**: Laboratories are linked to specific **Django Groups**, enforcing access control for different users.
- **Role Assignments**:
  - **Admins**: Full access to the **Django Admin Panel** for managing roles, metadata, and system-wide settings.
  - **Data_Curators**: Access to their assigned laboratory’s data, with permission to delete and modify existing metadata.
  - **Pipelines**: Access to pipeline interface (Jenkins) (Work in Progress).
  - **Guests**: Limited access to public metadata and the homepage, and create new metadata (like add a sample).

---

## **Adding a New Laboratory Model and Custom Sample Page**

To extend the **PRP CDM app** with a new laboratory and connect it with a custom sample form and report page in the **Home app**, follow these steps:

### **0. Pull Request Setup**
- Clone the repository and create a **meaningful feature branch** dedicated to your laboratory addition in this form add_laboratory/name_of_the_lab.

### **1. Create the Laboratory Model**
- In `decos/decos_webapp/PRP_CDM_app/models/laboratory_models/`, create a new file with a name like:
```
name_of_the_laboratory.py
```

- Use lowercase letters, no special characters; replace spaces with underscores.  
- Inside the file, define two classes:
  - `Name_Of_The_LaboratorySamples(Samples)` → for custom sample metadata.
  - `Name_Of_The_LaboratoryMetadata(models.Model)` → for metadata read from the formatted JSON file (WIP).  
- Add all required custom fields, using the existing laboratory models as examples.

### **2. Apply Database Migrations**
- Update the PRP-CDM database schema:

```bash
./dev_make_and_apply_migrations.sh
```

or manually:

```bash
python manage.py makemigrations
python manage.py migrate --database prpmetadata-db
```

### **3. Create Custom Sample Templates**

* Add a sample input form in:

  ```
  decos/decos_webapp/home/templates/home/forms/name_of_the_lab_form.html
  ```

* Add a report include template in:

  ```
  decos/decos_webapp/home/templates/home/sample_pages/includes/name_of_the_lab_report.html
  ```

* Use existing laboratory templates as references.

### **4. Register the Laboratory in the Admin Interface**

* Access the Django Admin: `http://<your-instance>/admin`.
* In the sidebar, select **Add Laboratory**, then provide:

  * **Name of the laboratory** (must match the filenames and class names, e.g. `"Name of the Lab"`).

    * Note: `_sanitize_lab_title(title: str)` in `decos/decos_webapp/home/forms.py` provides some normalization.
  * **Short description**.
* Assign the laboratory to the appropriate **user roles** in:
  [https://decos.areasciencepark.it/admin/users/](https://decos.areasciencepark.it/admin/users/)

### **5. Test the Laboratory**

* Switch to the new laboratory context.
* Create a new sample and verify:

  * It appears in the **sample list**.
  * The sample detail view renders correctly with the custom report template.

### **6. Deploy to Pre-Stage Production for testing**

* Bring down the development stack:

  ```bash
  docker compose -f docker-compose-dev.yaml down
  ```

* Install clean production mode:

  ```bash
  ./install_clean_production_mode.sh
  ```

* If debugging is required, temporarily set:

  ```python
  DEBUG = True
  ```

  in `settings/production.py`.

### **7. Pull Request**

* Commit your changes to the feature branch.
* Open a **Pull Request** on GitHub for review and integration.
* A code maintainer will review the code and if approved integrated in the main dev/production pipeline


## **6. License**

The **DECOS Webapp** is licensed under the **MIT License**.

### **Third-Party Licenses**
- **Django**: BSD License
- **Gunicorn**: MIT License
- **Debugpy**: MIT License
- **psycopg2-binary**: LGPL License
- **django-allauth**: MIT License
- **MinIO**: Apache License 2.0

