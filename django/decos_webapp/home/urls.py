from django.urls import path
from .views import user_data_view, switch_lab_view

app_name = 'home'

urlpatterns = [
    path('user-data/', user_data_view, name='user_data'),
    path('switch-laboratory/', switch_lab_view, name='switch-laboratory'),
]