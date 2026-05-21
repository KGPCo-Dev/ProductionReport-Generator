from django.urls import path
from . import views

app_name = 'cutting_machine_assignation'

urlpatterns = [
    path('', views.cutting_machine_assignation_view, name='machine_assignation'),
    path('api/search-order/', views.get_requested_order),
    path('api/save-assignation/', views.save_machine_assignation),
]