# models.py - DECOS System Metadata Catalog Model Documentation

## Overview

The `models.py` module is part of the DECOS system within a Django Wagtail-based web application. It provides data models to support the development of an experiment metadata catalog for life sciences laboratories participating in the PRP\_CDM\_app ecosystem. The module defines custom Wagtail pages and data management components that facilitate data entry, editing, catalog visualization, and the contextual linking of experimental data across samples, instruments, research results, and related metadata.

## Key Features

- **Wagtail Page Models:** Custom page types for data management, including sample entries, instruments, research results, and laboratory metadata.
- **Site-wide Settings:** Configurable header, footer, and API integration settings.
- **Sample-Driven Metadata Catalog:** Pages designed to enable sample-centric data entry and visualization.
- **Experiment Reporting:** Dedicated pages to display experiment metadata reports, linking samples, instruments, and results.
- **Pagination and Filtering:** Built-in support for paginated result views and laboratory-specific data filtering.

## Class Reference

### Page Models

| Class Name                     | Type                  | Description                                                                                                                                  |
| ------------------------------ | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `EditSamplePage`               | `wagtail.models.Page` | Provides an interface to **edit sample entries**, typically accessed from `SampleListPage`.                                                  |
| `SamplePage`                   | `wagtail.models.Page` | Displays the **page to add a new sample** with metadata entry.                                                                               |
| `SampleListPage`               | `wagtail.models.Page` | Lists research results with filtering and pagination capabilities, display minIO object location, elab and jenkins pipeline connections.                               |
| `InstrumentsPage`              | `wagtail.models.Page` | **Test page for instrument data** within the experiment metadata catalog context.                                                            |
| `PipelinesPage`                | `wagtail.models.Page` | Displays **pipelines related to laboratory workflows and data processing steps**.                                                            |
| `ResultsPage`                  | `wagtail.models.Page` | Displays a **detailed view of a research result**, **filtered by laboratory and result ID**, supporting pagination.                          |
| `ResultsListPage`              | `wagtail.models.Page` | **Lists research results with filtering and pagination capabilities, linked to experiment medata report page**. |
| `ExperimentMetadataReportPage` | `wagtail.models.Page` | Presents **detailed experiment metadata**, **linking samples, instruments, and lab DMP** for a comprehensive view.                           |

### Site Settings Models

| Class Name       | Type                   | Description                                                                                                    |
| ---------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------- |
| `HeaderSettings` | `wagtail.models.Model` | Configures **site-wide header elements**, such as logos and navigation links.                                  |
| `FooterSettings` | `wagtail.models.Model` | Defines **site-wide footer content**, including contact information and footer links.                          |
| `ApiSettings`    | `wagtail.models.Model` | Manages **external API integration settings**, enabling interoperability with laboratory systems and services. |

## Integration and Dependencies

This module interacts with the broader DECOS system, specifically:

- **PRP\_CDM\_app:**
  - `forms`: Provides user input mechanisms for sample entries, research results, and instrument data.
  - `models`: Supports data persistence and contextual linking of samples, results, instruments, and laboratory metadata.

## Usage

### Creating a New Wagtail Page with a Custom `serve()` Method

1. **Define the Page Model:**

   Create a new Django model that inherits from `wagtail.models.Page`. This model represents your custom page type.

   ```python
   from django.db import models
   from wagtail.models import Page

   class CustomPage(Page):
       content = models.TextField()

       content_panels = Page.content_panels + [
           FieldPanel('content'),
       ]
   ```

2. **Override the ************`serve()`************ Method:**

   The `serve()` method handles HTTP requests for the page. By overriding it, you can customize the response. For example, to return a simple HTTP response:

   ```python
   from django.http import HttpResponse

   class CustomPage(Page):
       def serve(self, request):
           return HttpResponse("This is a custom response for CustomPage.")
   ```

   Alternatively, to render a template with context:

   ```python
   from django.shortcuts import render

   class CustomPage(Page):
       def serve(self, request):
           context = self.get_context(request)
           return render(request, 'custom_page_template.html', context)
   ```

3. **Create a Template:**

   Ensure you have a corresponding template (e.g., `custom_page_template.html`) in your templates directory to render the page's content.

4. **Add the Page to the Wagtail Admin:**

   Register the new page model so it appears in the Wagtail admin interface, allowing editors to create and manage pages of this type.

## License

This module is part of the DECOS system and is licensed under the MIT License. See the `LICENSE` file in the project root for details.

## Authors

Developed by **Marco Prenassi** and **Cecilia Zagni**, Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy.

