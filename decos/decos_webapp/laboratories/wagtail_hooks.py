from django.urls import path, reverse

from .views import AddLabView, ModifyLabView, DeleteLabView
from wagtail import hooks
from wagtail.admin.menu import MenuItem


@hooks.register('register_admin_urls')
def register_add_laboratory_url():
    return [
        path('add-laboratory/', AddLabView, name='add-laboratory'),
        path("add-laboratory/<lab_id>/modify/", ModifyLabView, name='lab-modify'),
        path("add-laboratory/<lab_id>/modify/delete/", DeleteLabView, name='lab-delete'),

    ]

@hooks.register('register_admin_menu_item')
def register_add_laboratory_menu_item():
    return MenuItem('Add Laboratory', reverse('add-laboratory'), icon_name='mail')