from django.urls import path, include, re_path
from django.contrib import admin
from django.views.generic import TemplateView
from .views import (
    CallbackView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/', include('api.urls', namespace='api')),
    re_path(r'^auth/', include('rest_framework_social_oauth2.urls')),
    re_path(r'^api-auth/', include('rest_framework.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
]
