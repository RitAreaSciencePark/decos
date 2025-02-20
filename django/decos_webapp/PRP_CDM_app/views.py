from django.shortcuts import render
from .ontology.common_data_model import Administration

def listDMPView(request):
    data = Administration.objects.all()
    context = {"customdata": data}
    return render(request, "home/customlist.html", context)


