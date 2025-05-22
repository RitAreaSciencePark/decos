# DECOS Webapp - Home App Tables Documentation

## Overview

This document provides documentation for the Django tables defined in the `tables.py` module of the DECOS Webapp Home App. These tables utilize the `django-tables2` package to facilitate interactive table representations of various models, supporting features such as row selection and custom rendering.

## License

**Copyright (c) 2025** Marco Prenassi, Cecilia Zagni  
**Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),**  
**Area Science Park, Trieste, Italy.**  
Licensed under the MIT License. See the `LICENSE` file in the project root for full license information.

## Table Implementations

### BaseInteractiveTable

**Description:**  
A base class for interactive tables supporting row click events. This class allows JavaScript-based row selection through custom attributes.

#### Implementation:
```python
class BaseInteractiveTable(tables.Table):
    hidden_field_id: str
    form_id: str
    record_field: str

    def __init__(self, *args, hidden_field_id=None, form_id=None, record_field='id', **kwargs):
        super().__init__(*args, **kwargs)
        self.hidden_field_id = hidden_field_id
        self.form_id = form_id
        self.record_field = record_field

    def get_row_attrs(self, record):
        record_value = getattr(record, self.record_field)
        return {
            "onClick": generate_row_click_handler(self.hidden_field_id, record_value, self.form_id)
        }
```

---

### ServiceRequestTable

**Description:**  
A table for displaying `ServiceRequests`, inheriting from `BaseInteractiveTable` to enable row selection.

#### Implementation:
```python
class ServiceRequestTable(BaseInteractiveTable):
    class Meta:
        model = ServiceRequests
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("sr_id", "proposal_id", "lab_id", "sr_status", "output_delivery_date")
```

---

### SamplesTable

**Description:**  
A table for displaying `Samples`, including a custom button column for additional actions.

#### Implementation:
```python
class SamplesTable(tables.Table):
    button_column = TemplateColumn(
        verbose_name=(' '),
        template_name='home/sample_pages/sample_page_button_column.html',
        orderable=False
    )

    class Meta:
        model = Samples
        template_name = "django_tables2/bootstrap.html"
        fields = ("sample_id", "sr_id", "sample_short_description", "sample_status", "sample_location")
```

---

### SamplesForResultsTable

**Description:**  
A table used for selecting `Samples` when assigning `Results`. Inherits row selection features from `BaseInteractiveTable`.

#### Implementation:
```python
class SamplesForResultsTable(BaseInteractiveTable):
    class Meta:
        model = Samples
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("sample_id", "sample_short_description")
```

---

### InstrumentsForResultsTable

**Description:**  
A table used for selecting `Instruments` when assigning `Results`. Supports interactive row selection.

#### Implementation:
```python
class InstrumentsForResultsTable(BaseInteractiveTable):
    class Meta:
        model = Instruments
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("instrument_id", "model", "vendor")
```

---

### ResultsTable

**Description:**  
A table for displaying `Results`, supporting interactive row selection via JavaScript.

#### Implementation:
```python
class ResultsTable(tables.Table):
    class Meta:
        model = Results
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("result_id", "main_repository", "article_doi")
        row_attrs = {
            "onClick": lambda record: f"document.getElementById('result_id_hidden').value = '{record.result_id}'; document.getElementById('result_selection').submit();"
        }
```

## Integration & Dependencies

- **PRP_CDM_app.models:** Defines the models used in these tables, including `ServiceRequests`, `Samples`, `Instruments`, and `Results`.
- **django-tables2:** Enables table-based representation and interactive UI features.
- **JavaScript row selection handlers:** Used to facilitate interactive selection of records.

## Authors

Developed by **Marco Prenassi** and **Cecilia Zagni**,  
Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),  
Area Science Park, Trieste, Italy.

