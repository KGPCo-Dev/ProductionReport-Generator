from django.urls import path
from . import views

app_name = 'live_dashboards'

urlpatterns = [
    path('', views.live_dashboards_view, name='live_dashboards'),
]
