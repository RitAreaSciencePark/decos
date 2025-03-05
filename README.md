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

2. **Start the Development Environment**  
   ```bash
   docker compose up -d
   ```

3. **Run the Installation Script**  
   For a **clean setup** (wiping databases and rebuilding containers), run:
   ```bash
   sh install_clean_debug_mode.sh
   ```

4. **Start Debugging**  
   Open **VS Code**, go to **Run and Debug** (`Ctrl+Shift+D`), and select **Python Debugger: Remote Attach** to start the server. When successful, you will see:
   ```
   Starting development server at http://0.0.0.0:8080/
   Quit the server with CONTROL-C.
   ```

5. **Access the Web Application**  
   Visit the application at:
   ```
   http://easydmp.localhost:8080
   ```

---

## **5. Security & Access Control**

The **DECOS Webapp** implements **Role-Based Access Control (RBAC)** to ensure secure data management.

- **Django Groups**: Laboratories are linked to specific **Django Groups**, enforcing access control for different users.
- **Role Assignments**:
  - **Admins**: Full access to the **Django Admin Panel** for managing roles, metadata, and system-wide settings.
  - **Researchers**: Access to their assigned laboratory’s data and research workflows.
  - **Guests**: Limited access to public metadata and the homepage.

---

## **6. License**

The **DECOS Webapp** is licensed under the **MIT License**.

### **Third-Party Licenses**
- **Django**: BSD License
- **Gunicorn**: MIT License
- **Debugpy**: MIT License
- **psycopg2-binary**: LGPL License
- **django-allauth**: MIT License
- **MinIO**: Apache License 2.0

