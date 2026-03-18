# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-18
# Description:
# This file defines table classes using django-tables2 for the Decos Webapp - Home App.
# It provides table representations for Proposals, ServiceRequests, Samples, Instruments, and Results models.
# The tables support interactive row selection and custom rendering where necessary.

from django_tables2 import tables, Column, TemplateColumn
from PRP_CDM_app.models.common_data_model import (
    ExperimentDMP,
    Proposals, 
    ServiceRequests, 
    Samples, 
    Instruments, 
    Results
)

# Utility function to generate JavaScript click handler for row selection
# TODO: Implement it (and integrate it in ResultsSamples)
def generate_row_click_handler(input_id: str, record_id: str, form_id: str) -> str:
    return f"handleRowClick('{input_id}', '{record_id}', '{form_id}')"

# Base class for interactive tables supporting row click events
class BaseInteractiveTable(tables.Table):
    hidden_field_id: str
    form_id: str
    record_field: str

    def __init__(self, *args, hidden_field_id=None, form_id=None, record_field='id', **kwargs):
        super().__init__(*args, **kwargs)
        self.hidden_field_id = hidden_field_id
        self.form_id = form_id
        self.record_field = record_field

    # Generates row attributes for JavaScript click event
    def get_row_attrs(self, record):
        record_value = getattr(record, self.record_field)
        return {
            "onClick": generate_row_click_handler(self.hidden_field_id, record_value, self.form_id)
        }

# Table for displaying Proposals with custom rendering

class ProposalsTable(tables.Table):
    # Custom column example (optional styling kept)
    proposal_id = tables.Column(
        empty_values=(),
        attrs={"th": {"id": "foo"}},
        verbose_name="Proposal ID"
    )

    def render_proposal_id(self, record):
        return f"uuid: {record.proposal_id}"

    def render_id(self, value):
        return f"<{value}>"

    class Meta:
        model = Proposals
        template_name = "django_tables2/bootstrap.html"

        # Show only the new fields (excluding scheduled_instrument_ids)
        fields = (
            "proposal_id",
            "title",
            "submission_date",
            "team_leader_first_name",
            "team_leader_last_name",
        )

        row_attrs = {
            "onClick": lambda record: (
                f"document.getElementById('proposal_id_hidden').value = '{record.proposal_id}'; document.getElementById('proposal_selection').submit();"
            )
        }

        orderable = True


# Table for Proposals supporting row selection
class ServiceRequestTable(BaseInteractiveTable):
    class Meta:
        model = Proposals
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("sr_id", "proposal_id", "lab_id", "sr_status", "output_delivery_date")

# Table for Samples with a button column for additional actions
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
        row_attrs = {
            "onClick": lambda record: f"if (!event.target.closest('[data-no-row-click]')) {{ document.getElementById('sample_id_hidden').value = '{record.sample_id}'; document.getElementById('sample_selection').submit(); }}"
        }

# Table for selecting Samples when assigning Results
class SamplesSelectionTable(BaseInteractiveTable):
    class Meta:
        model = Samples
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("sample_id", "sample_short_description")
        row_attrs = {
            "onClick": lambda record: f"document.getElementById('sample_id').value = '{record.sample_id}'; document.getElementById('sample_selection').submit();"        
            # "onClick": lambda record: f'alert("I am an alert box!")',
        }

# Table for selecting Instruments when assigning Results
class InstrumentsSelectionTable(BaseInteractiveTable):
    class Meta:
        model = Instruments
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("instrument_id", "instrument_name", "institution")
        row_attrs = {
        "onClick": lambda record: f"document.getElementById('instrument_id_hidden').value = '{record.instrument_id}'; document.getElementById('instrument_selection').submit();"
        # "onClick": lambda record: f'alert("I am an alert box!")',
        }

# Table for displaying Results supporting row selection
class ResultsTable(tables.Table):
    button_column = TemplateColumn(
    verbose_name=(' '),
    template_name='home/lab_management_pages/results_button_column.html',
    orderable=False
    )
    class Meta:
        model = Results
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("result_id", "main_repository", "article_doi")
        row_attrs = {
            "onClick": lambda record: f"document.getElementById('result_id_hidden').value = '{record.result_id}'; document.getElementById('result_selection').submit();"
        }

# Table for displaying ExperimentDMP supporting row selection
class ExperimentDMPTable(tables.Table):
    button_column = TemplateColumn(
    verbose_name=(' '),
    template_name='home/lab_management_pages/experiment_dmp_page_button_column.html',
    orderable=False
    )
    class Meta:
        model = ExperimentDMP
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("experiment_dmp_id", "experiment_title", "principal_investigator")
        row_attrs = {
            "onClick": lambda record: f"document.getElementById('experiment_dmp_id_hidden').value = '{record.experiment_dmp_id}'; document.getElementById('experiment_dmp_selection').submit();"
        }