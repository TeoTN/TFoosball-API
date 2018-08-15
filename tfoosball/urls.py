from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView
from .views import (
    CallbackView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework_social_oauth2.urls')),
    path('api/', include('api.urls', namespace='api')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
]
