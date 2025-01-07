from django import forms
from PRP_CDM_app.models import Laboratories

class AddNewLabForm(forms.ModelForm):
    class Meta:
            model = Laboratories
            fields = ['lab_id', 'description']

class ModifyLabForm(forms.ModelForm):
    class Meta:
            model = Laboratories
            fields = ['description']