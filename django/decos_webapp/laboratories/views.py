from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.utils import timezone
from .forms import AddNewLabForm, ModifyLabForm
from django.contrib.auth.models import Group
from django.db.models import Model
from PRP_CDM_app.models.common_data_model import Laboratories


def AddLabView(request):

    if request.method == 'POST':
        form = AddNewLabForm(data=request.POST)
        if form.is_valid():
            lab_id = form.cleaned_data["lab_id"]
            try:
                lab = Group.objects.get(name=lab_id)
            except Group.DoesNotExist as e:
                lab = Group(name=form.cleaned_data["lab_id"],laboratory= True)
                lab.save()
            form.save()
        else:
            errors = form.errors
            return render(request, 'error_page.html', {
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'errors': form.errors,
            })
    
    form = AddNewLabForm()
    if Group.objects.filter(laboratory = True ).count() != Laboratories.objects.count():
        return render(request, 'error_page.html', {
                # We pass the data to the thank you page, data.datavarchar and data.dataint!
                'errors': {'Group Mismatch' : 'Laboratories and Groups are mismatched, contact an Administrator!'},
            })
    laboratories = list(Laboratories.objects.all())
    return render(request, 'laboratory_form.html', {'form' : form, 'laboratories' : laboratories})

def ModifyLabView(request, lab_id):
    if request.method == "POST":
        form = ModifyLabForm(data=request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.lab_id = lab_id
            data.save()
            return redirect("/admin/add-laboratory/")

    data = Laboratories.objects.get(pk=lab_id)
    form = ModifyLabForm(instance=data)
    return render(request, 'edit_laboratory_form.html', {'lab_name' : lab_id, 'form' : form})

def DeleteLabView(request, lab_id):
    if request.method == "POST":
        if(request.POST['delete'] == 'DELETE') and request.POST['security_question'] == lab_id:
            lab_to_delete = Laboratories.objects.get(pk=lab_id)
            group_to_delete = Group.objects.get(pk=Group.objects.filter(name=lab_id).values().first()['id'])
            lab_to_delete.delete()
            group_to_delete.delete()
            return redirect("/admin/add-laboratory/")
    data = Laboratories.objects.get(pk=lab_id)
    return render(request, 'delete_laboratory_form.html', {'lab_name' : lab_id})
    
