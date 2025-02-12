from django.db import models
from django.contrib.auth.models import User

class API_Tokens(models.Model):
        # TODO: manage this secret!!!!
    user_id = models.CharField(max_length=50)
    laboratory = models.CharField(max_length=50)
    elab_token = models.CharField(max_length=128, null=True, blank=True)
    jenkins_token = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        db_table= 'API_tokens'.lower()
        app_label = 'home'
