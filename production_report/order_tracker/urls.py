from django.urls import path
from . import views

app_name = 'order_tracker'

urlpatterns = [ 
    path('',  views.order_tracker_view, name = 'order_tracker'),
    path('update-delivery-date/', views.update_delivery_date, name='update_delivery_date'),
 ]