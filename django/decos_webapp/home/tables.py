from django_tables2 import tables, Column, TemplateColumn

from PRP_CDM_app.models import Proposals,ServiceRequests,Samples, Instruments, Results

class ProposalsTable(tables.Table):
    proposal_id = Column(empty_values=(),attrs={"th": {"id": "foo"}},verbose_name="id of the proposal")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render_proposal_id(self, record):
        return f"uuid: {record.proposal_id}"

    def render_id(self, value):
        return f"<{value}>"

    class Meta:
        model = Proposals
        template_name = "django_tables2/bootstrap.html"
        fields = ("proposal_date","proposal_filename","proposal_id", "proposal_status", "proposal_feasibility" )
        row_attrs = {
        "onClick": lambda record: f"document.getElementById('proposalIdBox').value = '{record.proposal_id}';"
        }
        orderable = True

class ServiceRequestTable(tables.Table):
    class Meta:
        model = ServiceRequests
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("sr_id","proposal_id","lab_id","sr_status","output_delivery_date")
        row_attrs = {
        "onClick": lambda record: f"document.getElementById('sr_id_hidden').value = '{record.sr_id}'; document.getElementById('sr_selection').submit();"
        }

class SamplesTable(tables.Table):
    button_column = TemplateColumn(verbose_name=(' '),
                                    template_name='home/sample_pages/sample_page_button_column.html',
                                    orderable=False)

    class Meta:
        model = Samples
        template_name = "django_tables2/bootstrap.html"
        fields = ("sample_id","sr_id","sample_short_description","sample_status","sample_location")


class SamplesForResultsTable(tables.Table):
    class Meta:
        model = Samples
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("sample_id","sample_short_description")
        row_attrs = {
        "onClick": lambda record: f"document.getElementById('sample_id_hidden').value = '{record.sample_id}'; document.getElementById('sample_selection').submit();"
        }

class InstrumentsForResultsTable(tables.Table):
    class Meta:
        model = Instruments
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("instrument_id","model","vendor")
        row_attrs = {
        "onClick": lambda record: f"document.getElementById('instrument_id_hidden').value = '{record.instrument_id}'; document.getElementById('instrument_selection').submit();"
        # "onClick": lambda record: f'alert("I am an alert box!")',
        }

class ResultsTable(tables.Table):
    class Meta:
        model = Results
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("result_id","main_repository","article_doi")
        row_attrs = {
        "onClick": lambda record: f"document.getElementById('result_id_hidden').value = '{record.result_id}'; document.getElementById('result_selection').submit();"
        # "onClick": lambda record: f'alert("I am an alert box!")',
        }