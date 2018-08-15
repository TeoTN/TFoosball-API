from django.urls import path, include

from api.routers import ExtendedDefaultRouter
from .views import (
    MemberViewSet,
    MatchViewSet,
    TeamViewSet,
    PlayerViewSet,
    WhatsNewViewSet,
    EventsViewSet,
)

app_name = 'api'
router = ExtendedDefaultRouter()
player_routes = router.register(r'players', PlayerViewSet, base_name='player')
team_routes = router.register(r'teams', TeamViewSet, base_name='team')
team_routes.register(r'members', MemberViewSet, base_name='team-member', parents_query_lookups=['team'])
team_routes.register(r'matches', MatchViewSet, base_name='team-matches', parents_query_lookups=['team'])
team_routes.register(r'events', EventsViewSet, base_name='team-events', parents_query_lookups=['team'])
whatsnew = router.register(r'whatsnew', WhatsNewViewSet, base_name='whatsnew')

urlpatterns = [
    path('', include(router.urls)),
]
