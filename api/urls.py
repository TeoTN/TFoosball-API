from django.conf.urls import url, include
from .views import (
    MemberViewSet,
    MatchViewSet,
    CountPointsView,
    UserLatestMatchesView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', MemberViewSet, base_name='member')
router.register(r'matches', MatchViewSet, base_name='match')

urlpatterns = [
    url(r'^matches/count-points/?$', CountPointsView.as_view(), name='count_points'),
    url(r'^users/(?P<username>[A-Za-z0-9_\-\.]+)/matches/?$', UserLatestMatchesView.as_view(), name='user_matches'),
    url(r'^', include(router.urls, namespace='api')),
]
