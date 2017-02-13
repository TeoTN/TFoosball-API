from django.conf.urls import url, include
from .views import (
    MemberViewSet,
    MatchViewSet,
    CountPointsView,
    UserLatestMatchesView,
    TeamViewSet,
)
from rest_framework.routers import DefaultRouter

team_router = DefaultRouter()
team_router.register(r'users', MemberViewSet, base_name='member')
team_router.register(r'matches', MatchViewSet, base_name='match')

router = DefaultRouter()
router.register(r'teams', TeamViewSet, base_name='team')

urlpatterns = [
    url(r'^(?P<team>[0-9a-zA-Z]+)/matches/count-points/?$', CountPointsView.as_view(), name='count_points'),
    url(r'^(?P<team>[0-9a-zA-Z]+)/users/(?P<username>[A-Za-z0-9_\-\.]+)/matches/?$', UserLatestMatchesView.as_view(), name='user_matches'),
    url(r'^', include(router.urls, namespace='api')),
    url(r'^(?P<team>[0-9a-zA-Z]+)/', include(team_router.urls, namespace='team-api')),
]
