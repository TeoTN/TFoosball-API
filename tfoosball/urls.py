from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from .views import (
    CallbackView,
    GoogleLoginView,
    UserViewSet,
    MatchViewSet,
    CountPointsView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'matches', MatchViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/google/$', GoogleLoginView.as_view(), name='g_login'),
    url(r'^auth/callback/?$', CallbackView.as_view(), name='auth_callback'),
    url(r'^api/matches/count-points/?$', CountPointsView.as_view(), name='count_points'),
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
]
