# Template File Structure - DECOS Webapp Home App

This document outlines the structure of the template files directory within the DECOS Webapp Home App module. It references the `models.py` documentation to illustrate how these templates correspond to specific Wagtail pages and data management views in the DECOS system.

## Root Path
```
django/decos_webapp/home/templates/
```

## Directory Structure
```
django/decos_webapp/home/templates/home
|-- admin_pages
|   |-- add_new_lab_page.html
|
|-- dmp_pages
|   |-- generic_dmp_view.html
|   |-- labdmp_page.html
|
|-- elabFTW
|   |-- experiment_template.html
|
|-- forms
|   |-- generic_form_page.html
|   |-- lage_form.html
|   |-- no_form.html
|
|-- lab_management_pages
|   |-- includes
|   |-- experiment_metadata_report_page.html
|   |-- instruments_page.html
|   |-- results_list_page.html
|   |-- results_page.html
|
|-- reports
|   |-- lage_form.html
|
|-- sample_pages
|   |-- edit_sample_page.html
|   |-- pipelines_page.html
|   |-- sample_list.html
|   |-- sample_page_button_column.html
|   |-- sample_page.html
|
|-- utility_pages
|   |-- user_data_page.html
|
|-- WIP_pages
|
|-- error_page.html
|-- home_page.html
|-- thank_you_page.html
```

## Template Descriptions

### Admin Pages
- **add_new_lab_page.html** - Admin interface for adding a new laboratory entry.

### DMP Pages
- **generic_dmp_view.html** - Generic view template for displaying DMP content.
- **labdmp_page.html** - Template for LabDMP page visualization.

### eLabFTW
- **experiment_template.html** - Template for viewing experiments integrated with eLabFTW.

### Forms
- **generic_form_page.html** - Template for displaying generic forms.
- **lage_form.html** - Template for the LAGE form.
- **no_form.html** - Template for displaying when no form is available.

### Lab Management Pages
- **experiment_metadata_report_page.html** - Template for displaying detailed experiment metadata report.
- **instruments_page.html** - Template for managing instrument data.
- **results_list_page.html** - Template for listing research results with pagination and filtering.
- **results_page.html** - Template for detailed research result view.

### Reports
- **lage_form.html** - Report template related to the LAGE form.

### Sample Pages
- **edit_sample_page.html** - Template for editing sample entries.
- **pipelines_page.html** - Template for viewing laboratory data processing pipelines.
- **sample_list.html** - Template for listing sample entries.
- **sample_page_button_column.html** - Partial template for rendering buttons in the sample page.
- **sample_page.html** - Template for viewing and adding sample entries.

### Utility Pages
- **user_data_page.html** - Template for displaying user-specific data.

### Other Pages
- **error_page.html** - Template for displaying error messages.
- **home_page.html** - Template for the Home Page.
- **thank_you_page.html** - Template for displaying a thank you message.

## Usage
These templates correspond to the custom Wagtail page models defined in `models.py`. Each template is associated with a specific page type or functional component, ensuring a structured and modular approach to rendering content within the DECOS Webapp Home App.

