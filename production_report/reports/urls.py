from django.urls import path
from . import views

app_name = 'report_generator'

urlpatterns = [ 
    path('', views.production_report_view, name = 'report_list'),
 ]