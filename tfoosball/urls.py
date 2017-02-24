from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from .views import (
    CallbackView,
    GoogleLoginView,
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^(?P<team>[0-9a-zA-Z]+)/rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/google/$', GoogleLoginView.as_view(), name='g_login'),
    url(r'^auth/callback/?$', CallbackView.as_view(), name='auth_callback'),
    url(r'^api/', include('api.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
]
