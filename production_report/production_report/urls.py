from django.contrib import admin
from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('production-report/', include('reports.urls')),
    path('order-tracker/', include('order_tracker.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [ 
        path('__debug__/', include(debug_toolbar.urls)),
     ] + urlpatterns
