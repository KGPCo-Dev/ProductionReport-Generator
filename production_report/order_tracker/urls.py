from django.urls import path
from . import views

app_name = 'order_tracker'

urlpatterns = [ 
    path('',  views.order_tracker_view, name = 'order_tracker'),
 ]