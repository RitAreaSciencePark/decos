from django.apps import AppConfig

class PrpCdmAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PRP_CDM_app'

    def ready(self):
        from .models.common_data_model import (
            Users,
            Laboratories,
            labDMP,
            Samples,
            Instruments,
            Results,
            ServiceRequests,
            ResultxSample,
            ResultxInstrument,
            ResultxLab,
            Proposals,
        )
        from .models.laboratory_models.lage import LageSamples
        from .models.laboratory_models.lame import LameSamples

        