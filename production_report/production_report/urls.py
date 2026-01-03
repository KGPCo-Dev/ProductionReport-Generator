"""
URL configuration for production_report project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from unicodedata import name
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from reports import views
from home.views import home_view
from order_tracker.views import order_tracker_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name ='home'),
    path('production-report/', views.production_report_view, name='production_report'),
    path('order-tracker/', order_tracker_view, name='order_tracker')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [ 
        path('__debug__/', include(debug_toolbar.urls)),
     ] + urlpatterns
