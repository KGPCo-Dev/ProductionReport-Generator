from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from rest_framework.authtoken import views as dfr_views
from reports.api.api_views import AllDataAPI, TableAPI

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('production-report/', include('reports.urls')),
    path('order-tracker/', include('order_tracker.urls')),
    path('api-token-auth/', dfr_views.obtain_auth_token),
    path('api/data/<str:table_name>/', TableAPI.as_view(), name='api_all_data'),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [ 
        path('__debug__/', include(debug_toolbar.urls)),
     ] + urlpatterns
