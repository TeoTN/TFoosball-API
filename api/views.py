from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .serializers import MatchSerializer, MemberSerializer, TeamSerializer
from tfoosball.models import Member, Match, Team


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class TeamViewSet(ModelViewSet):
    serializer_class = TeamSerializer
    allowed_methods = [u'GET', u'POST', u'OPTIONS']

    def get_queryset(self):
        return self.request.user.teams


class MemberViewSet(ModelViewSet):
    serializer_class = MemberSerializer
    lookup_field = 'username'
    lookup_value_regex = '[A-Za-z0-9_\-\.]+'

    def get_queryset(self):
        return Member.objects.filter(player__hidden=False, team__domain=self.kwargs['team'])


class MatchViewSet(ModelViewSet):
    serializer_class = MatchSerializer
    allowed_methods = [u'GET', u'POST', u'PUT', u'PATCH', u'DELETE', u'OPTIONS']
    pagination_class = StandardPagination

    def get_queryset(self):
        domain = self.kwargs['team']
        queryset = Match.objects.filter(
            Q(red_att__team__domain=domain) |
            Q(red_def__team__domain=domain) |
            Q(blue_att__team__domain=domain) |
            Q(blue_def__team__domain=domain)
        )
        queryset = queryset.order_by('-date')
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(MatchViewSet, self).list(request, args, kwargs)
        response.data['page'] = request.GET.get('page', 1)
        response.data['page_size'] = request.GET.get('page_size', StandardPagination.page_size)
        return response


class CountPointsView(APIView):
    def get(self, request, *args, **kwargs):
        data = {k+'_id': v for k, v in request.GET.items()}
        match = Match(**data, red_score=0, blue_score=10)
        try:
            result1 = abs(match.calculate_points()[0])
        except (Match.red_att.RelatedObjectDoesNotExist,
                Match.red_def.RelatedObjectDoesNotExist,
                Match.blue_att.RelatedObjectDoesNotExist,
                Match.blue_def.RelatedObjectDoesNotExist):
            return Response({'detail': 'Players have not been provided'}, status=406)
        match = Match(**data, red_score=10, blue_score=0)
        result2 = abs(match.calculate_points()[0])
        return Response({'blue': result1, 'red': result2})


class UserLatestMatchesView(ListAPIView):
    pagination_class = StandardPagination
    serializer_class = MatchSerializer
    allowed_methods = [u'GET', u'OPTIONS']

    def get_queryset(self):
        username = self.kwargs['username']
        team = self.kwargs['team']
        user = get_object_or_404(Member, username=username, team__domain=team)
        return user.get_latest_matches()

    def list(self, request, *args, **kwargs):
        response = super(UserLatestMatchesView, self).list(request, args, kwargs)
        response.data['page'] = request.GET.get('page', 1)
        response.data['page_size'] = request.GET.get('page_size', StandardPagination.page_size)
        return response
