# DECOS Webapp - Project Structure Overview

## Overall Description

The Home App is an integral component of the DECOS (Digital Ecosystem) within the Pathogen Readiness Platform (PRP\@CERIC). It is responsible for managing the web-based user interface of the DECOS system, facilitating interaction with the underlying data infrastructure. The Home App's database structure is maintained within the `decos_metadata_db` relational database, ensuring robust data management and retrieval capabilities for life sciences laboratories.

## Root Directory

```
django/decos_webapp/
```

## Home App Structure

```
django/decos_webapp/home/
|-- docs/
|-- static/
|-- templates/
|-- admin_custom.py
|-- auth.py
|-- decos_elab.py
|-- decos_jenkins.py
|-- forms.py
|-- models.py
|-- secrets_models.py
|-- tables.py
|-- urls.py
|-- views.py
```

### **Directories**

- **docs/** – Documentation files related to the Home App.
- **static/** – Contains static assets such as CSS stylesheets and JavaScript files.
- **templates/** – Holds Django templates for rendering UI pages.

### **Python Modules**

- **admin\_custom.py** – Custom Wagtail admin panel configurations.
- **auth.py** – User authentication and session management.
- **decos\_elab.py** – Integration with the eLabFTW experiment tracking system.
- **decos\_jenkins.py** – Pipeline management and Jenkins integration.
- **forms.py** – Defines Django forms for user input and metadata collection.
- **models.py** – Wagtail-based data models for metadata cataloging.
- **secrets\_models.py** – Handles sensitive data storage and API credentials.
- **tables.py** – Implements interactive tables for data representation.
- **urls.py** – Maps URL endpoints to corresponding views.
- **views.py** – Handles HTTP requests and renders templates.

## **Static File Structure**

```
django/decos_webapp/home/static/
|-- css/
    |-- forms/
    |   |-- labdmp_page.css
    |   |-- lage_form.css
    |   |-- lame_form.css
    |-- home_page.css
    |-- list_page.css
    |-- thank_you_page.css
    |-- user_data.css
```

## **Templates Folder Structure**

```
django/decos_webapp/home/templates/home/
|-- admin_pages/
|-- dmp_pages/
|-- elabFTW/
|-- forms/
|-- lab_management_pages/
|-- reports/
|-- sample_pages/
|-- utility_pages/
|-- WIP_pages/
|-- error_page.html
|-- home_page.html
|-- thank_you_page.html
```

### **Key Template Categories**

- **Admin Pages** – Templates for administrative interfaces.
- **DMP Pages** – Templates related to Data Management Plans.
- **Forms** – Templates for rendering dynamic forms.
- **Lab Management Pages** – Templates for handling metadata reports and instruments.
- **Sample Pages** – Templates for managing laboratory sample data.
- **Utility Pages** – Templates for displaying user-specific data.


## **Templates File Structure**

```
django/decos_webapp/home/templates/home/
|-- admin_pages/
|   |-- add_new_lab_page.html
|-- dmp_pages/
|   |-- generic_dmp_view.html
|   |-- labdmp_page.html
|-- elabFTW/
|   |-- experiment_template.html
|-- forms/
|   |-- generic_form_page.html
|   |-- lage_form.html
|-- lab_management_pages/
|   |-- experiment_metadata_report_page.html
|   |-- instruments_page.html
|   |-- results_list_page.html
|   |-- results_page.html
|-- sample_pages/
|   |-- edit_sample_page.html
|   |-- pipelines_page.html
|   |-- sample_list.html
|   |-- sample_page_button_column.html
|   |-- sample_page.html
|-- utility_pages/
|   |-- user_data_page.html
|-- error_page.html
|-- home_page.html
|-- thank_you_page.html
```

### **Template Descriptions**

- **admin\_pages/add\_new\_lab\_page.html** – Admin interface for adding a new laboratory entry.
- **dmp\_pages/generic\_dmp\_view\.html** – Generic view for displaying Data Management Plan (DMP) content.
- **dmp\_pages/labdmp\_page.html** – Template for the LabDMP page visualization, linked to research data.
- **elabFTW/experiment\_template.html** – Displays experiment details from the eLabFTW system.
- **forms/generic\_form\_page.html** – Renders dynamic lab-aspecific forms (default form if not implemented with [labname]_form.html, see lage_form.html).
- **forms/lage\_form.html** – Template for the LAGE lab form submission.
- **lab\_management\_pages/experiment\_metadata\_report\_page.html** – Shows linked metadata for experiments.
- **lab\_management\_pages/instruments\_page.html** – Displays a list of available laboratory instruments.
- **lab\_management\_pages/results\_list\_page.html** – Lists research results with filtering options.
- **lab\_management\_pages/results\_page.html** – Displays detailed information about a research result.
- **sample\_pages/edit\_sample\_page.html** – Allows editing of sample metadata.
- **sample\_pages/pipelines\_page.html** – Displays available data processing pipelines.
- **sample\_pages/sample\_list.html** – Lists all sample entries in the system.
- **sample\_pages/sample\_page\_button\_column.html** – Renders action buttons within sample pages.
- **sample\_pages/sample\_page.html** – Page for inputting and viewing sample data.
- **utility\_pages/user\_data\_page.html** – Displays user-specific data and settings.
- **error\_page.html** – Handles system error messages and alerts.
- **home\_page.html** – Main landing page of the web application.
- **thank\_you\_page.html** – Confirmation page after successful form submission.

Each template is associated with Wagtail models defined in `models.py`, ensuring structured data management and visualization in the DECOS system.

## **Models Overview**

```
models.py
|-- SamplePage (wagtail.models.Page)
|-- SampleListPage (wagtail.models.Page)
|-- InstrumentsPage (wagtail.models.Page)
|-- PipelinesPage (wagtail.models.Page)
|-- ResultsPage (wagtail.models.Page)
|-- ExperimentMetadataReportPage (wagtail.models.Page)
|-- HeaderSettings (wagtail.models.Model)
|-- FooterSettings (wagtail.models.Model)
|-- ApiSettings (wagtail.models.Model)
```

The `models.py` file defines structured Wagtail page models that support metadata cataloging and data entry for research experiments. These models provide structured storage and retrieval mechanisms for samples, instruments, research results, and laboratory metadata.

The `models.py` file defines structured Wagtail page models that support metadata cataloging and data entry for research experiments. These models provide structured storage and retrieval mechanisms for samples, instruments, research results, and laboratory metadata.

- **SamplePage** – Page to input and view sample data.
- **SampleListPage** – Lists samples with filtering and pagination.
- **InstrumentsPage** – Page to manage and display laboratory instruments.
- **PipelinesPage** – Page showing laboratory data processing pipelines.
- **ResultsPage** – Displays detailed research result data.
- **ExperimentMetadataReportPage** – Aggregates sample, instrument, and result metadata into a report.
- **HeaderSettings** – Configures global site header content.
- **FooterSettings** – Configures global site footer content.
- **ApiSettings** – Stores external API integration settings.

```
models.py
|-- SamplePage (wagtail.models.Page)
|-- SampleListPage (wagtail.models.Page)
|-- InstrumentsPage (wagtail.models.Page)
|-- PipelinesPage (wagtail.models.Page)
|-- ResultsPage (wagtail.models.Page)
|-- ExperimentMetadataReportPage (wagtail.models.Page)
|-- HeaderSettings (wagtail.models.Model)
|-- FooterSettings (wagtail.models.Model)
|-- ApiSettings (wagtail.models.Model)
```

## **Tables Overview**

```
tables.py
|-- BaseInteractiveTable (tables.Table)
|-- ServiceRequestTable (BaseInteractiveTable)
|-- SamplesTable (tables.Table)
|-- SamplesForResultsTable (BaseInteractiveTable)
|-- InstrumentsForResultsTable (BaseInteractiveTable)
|-- ResultsTable (tables.Table)
```

The `tables.py` module implements Django Tables2-based interactive tables for managing research metadata and facilitating data selection within the web UI.

The `tables.py` module implements Django Tables2-based interactive tables for managing research metadata and facilitating data selection within the web UI.

- **BaseInteractiveTable** – Base table class with row selection support.
- **ServiceRequestTable** – Displays service request records interactively.
- **SamplesTable** – Displays sample data with action buttons.
- **SamplesForResultsTable** – Enables selection of samples for result assignment.
- **InstrumentsForResultsTable** – Enables selection of instruments for result assignment.
- **ResultsTable** – Displays research result data interactively.

```
tables.py
|-- BaseInteractiveTable (tables.Table)
|-- ServiceRequestTable (BaseInteractiveTable)
|-- SamplesTable (tables.Table)
|-- SamplesForResultsTable (BaseInteractiveTable)
|-- InstrumentsForResultsTable (BaseInteractiveTable)
|-- ResultsTable (tables.Table)
```

## **Forms Overview**

```
forms.py
|-- LabSwitchForm (forms.Form)
|-- DMPform (forms.ModelForm)
|-- UserDataForm (forms.ModelForm)
|-- InstrumentsForm (forms.ModelForm)
|-- ResultsForm (forms.ModelForm)
|-- AddNewLabForm (forms.ModelForm)
|-- APITokenForm (forms.ModelForm)
|-- ProposalSubmissionForm (forms.ModelForm)
|-- SRSubmissionForm (forms.ModelForm)
|-- SRForSampleForm (forms.ModelForm)
```

The `forms.py` module defines Django forms for handling dynamic data entry, user submissions, and laboratory metadata management within the system.

The `forms.py` module defines Django forms for handling dynamic data entry, user submissions, and laboratory metadata management within the system.

- **LabSwitchForm** – Enables users to switch between laboratories.
- **DMPform** – Handles Data Management Plan (DMP) entries.
- **UserDataForm** – Manages user-specific metadata.
- **InstrumentsForm** – Collects instrument-related data.
- **ResultsForm** – Records research result entries.
- **AddNewLabForm** – Adds new laboratory records via the admin panel.
- **APITokenForm** – Manages API tokens for lab systems.
- **ProposalSubmissionForm** – Handles proposal data submissions.
- **SRSubmissionForm** – Submits service request data.
- **SRForSampleForm** – Links samples to service requests.

```
forms.py
|-- LabSwitchForm (forms.Form)
|-- DMPform (forms.ModelForm)
|-- UserDataForm (forms.ModelForm)
|-- InstrumentsForm (forms.ModelForm)
|-- ResultsForm (forms.ModelForm)
|-- AddNewLabForm (forms.ModelForm)
|-- APITokenForm (forms.ModelForm)
|-- ProposalSubmissionForm (forms.ModelForm)
|-- SRSubmissionForm (forms.ModelForm)
|-- SRForSampleForm (forms.ModelForm)
```

## **Authentication System**

```
auth.py
|-- UserRegistrationForm (allauth.account.forms.SignupForm)
|-- UserLoginForm (allauth.account.forms.LoginForm)
```

The `auth.py` module extends Django Allauth authentication to ensure secure user management and integration with the DECOS system.

The `auth.py` module extends Django Allauth authentication to ensure secure user management and integration with the DECOS system.

- **UserRegistrationForm** – Extends Allauth to register users and create `Users` entries.
- **UserLoginForm** – Extends Allauth to log in users and validate/create `Users` entries.

```
auth.py
|-- UserRegistrationForm (allauth.account.forms.SignupForm)
|-- UserLoginForm (allauth.account.forms.LoginForm)
```

## **External Integrations**

- **Wagtail** – Manages structured content and metadata cataloging.
- **eLabFTW** – Integrates electronic laboratory notebook functionalities.
- **Jenkins** – Handles data processing pipelines.
- **MinIO** – Supports object storage and research data retrieval.

## **License**

This project is licensed under the MIT License. See the `LICENSE` file in the project root for details.

## **Authors**

Developed by **Marco Prenassi** and **Cecilia Zagni**, Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy.

