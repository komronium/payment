from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='schema-swagger-ui'),
    path('', include('apps.payments.urls')),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='schema-redoc'),
]
