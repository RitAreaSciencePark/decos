# forms.py - DECOS System Form Management Documentation

## Overview

This `forms.py` module is part of the DECOS system within a Django-based web application. It provides dynamic form management capabilities tailored for life sciences laboratories participating in the PRP_CDM_app ecosystem. The module enables user-driven sample form creation, laboratory switching, data entry, and API token management, ensuring a flexible and lab-specific data collection process.

## Key Features

- **Dynamic Form Generation:** Dynamically creates laboratory-specific sample forms based on user selections.
- **Custom Widgets:** Integrates custom widgets such as `BooleanIfWhat` and `MultiChoicheAndOtherWidget` for enhanced data input.
- **Lab Context Awareness:** Filters data based on the user's associated laboratories, ensuring context-specific form fields and choices.
- **Token and Proposal Management:** Facilitates API token management and supports workflows for proposal and service request submissions.

## Class and Function Reference

### Forms

| Class Name               | Type              | Description                                                                                              |
| ------------------------ | ----------------- | -------------------------------------------------------------------------------------------------------- |
| `LabSwitchForm`          | `forms.Form`      | Allows users to switch between laboratories, dynamically generating lab choices based on user access.    |
| `DMPform`                | `forms.ModelForm` | Manages Data Management Plan (DMP) entries for laboratories, integrating Boolean widgets for key fields. |
| `UserDataForm`           | `forms.ModelForm` | Handles user data within the `decos_metadata_db` ontology.                                               |
| `InstrumentsForm`        | `forms.ModelForm` | Collects instrument data entries, initially designed as a mockup/test form before EPIRO integration.     |
| `ResultsForm`            | `forms.ModelForm` | Captures core result data, including repository and article DOI details.                                 |
| `AddNewLabForm`          | `forms.ModelForm` | Supports the addition of new laboratories via the admin interface.                                       |
| `APITokenForm`           | `forms.ModelForm` | Facilitates API token management, with laboratory choices filtered based on user group memberships.      |
| `ProposalSubmissionForm` | `forms.ModelForm` | Handles proposal submission data, excluding user and status fields.                                      |
| `SRSubmissionForm`       | `forms.ModelForm` | Supports service request submission, with user-specific queryset adjustments.                            |
| `SRForSampleForm`        | `forms.ModelForm` | Links samples to service requests, filtering service requests based on the user's proposals.             |

### Functions

| Function Name                                                                          | Description                                                                                                |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `form_orchestrator(user_lab, request, filerequest, get_instance)`                      | Dynamically generates sample forms based on the selected laboratory, leveraging `FormsDefinition` classes. |
| `get_exclude_and_widgets(form_class, form_model)`                                      | Retrieves field exclusions and widget configurations for dynamic forms.                                    |
| `form_factory(form_model, widgets_list, request, filerequest, exclude_list, instance)` | Generates custom `ModelForm` classes based on provided models, widgets, and input data.                    |

## Integration and Dependencies

This module interacts with several key components within the DECOS system:

- **PRP_CDM_app:**
  - `fields`: Provides custom field types and widgets.
  - `forms`: Supplies form definitions for dynamic sample forms.
  - `models`: Supports form data collection using `Users`, `Proposals`, `ServiceRequests`, `Laboratories`, `Samples`, `Instruments`, `Results`, and `labDMP` models.
- **secrets_models:**
  - `API_Tokens`: Handles secure token management.

## Usage

### 1. Dynamic Sample Form Handling

This section covers the use of `form_orchestrator` and `form_factory` to dynamically create sample forms based on the laboratory context.

Example - Handling POST requests to submit a new sample:

```python
if request.method == 'POST':
    forms = form_orchestrator(
        user_lab=lab.lab_id,
        request=request.POST,
        filerequest=request.FILES,
        get_instance=False
    )
    success, result = self.process_forms(
        forms,
        lab=lab,
        request=request,
        generate_sample_id=True
    )

    if success:
        return render(request, 'home/thank_you_page.html', {'page': self, 'data': result})

    sr_id = request.POST.get("sr_id_hidden", "internal")
    context = {
        'forms': forms,
        'lab': lab.lab_id,
        'sr_id': sr_id,
        'errors': result
    }
    return render(request, 'home/sample_form_page.html', context)
```

### 2. Fixed Forms for Standard Data Entry

This section illustrates the use of predefined forms like `ResultsForm` for standard data entry, such as recording research outcomes.

Example:

```python
if request.method == 'POST':
    form = ResultsForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('results_list')

    context = {'form': form}
    return render(request, 'home/results_form.html', context)
```

## License

This module is part of the DECOS system and is licensed under the MIT License. See the `LICENSE` file in the project root for details.

## Authors

Developed by **Marco Prenassi** and **Cecilia Zagni**, Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT), Area Science Park, Trieste, Italy.

