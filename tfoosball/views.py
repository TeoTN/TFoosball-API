from django.views.generic import TemplateView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Player, Match
from .serializers import UserSerializer, MatchSerializer
import os


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class CallbackView(TemplateView):
    template_name = 'callback.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['access_token'] = request.GET.get('access_token')
        context['token_type'] = request.GET.get('token_type')
        context['expires_in'] = request.GET.get('expires_in')
        context['FRONTEND_CLIENT'] = os.environ.get('FRONTEND_CLIENT', 'http://localhost:3000/')
        return self.render_to_response(context)


class UserViewSet(ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class MatchViewSet(ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class CountPointsView(APIView):
    def get(self, request, *args, **kwargs):
        data = {k+'_id': v for k, v in request.GET.items()}
        match = Match(**data, red_score = 0, blue_score = 10)
        try:
            result1 = abs(match.calculate_points()[0])
        except (Match.red_att.RelatedObjectDoesNotExist,
                Match.red_def.RelatedObjectDoesNotExist,
                Match.blue_att.RelatedObjectDoesNotExist,
                Match.blue_def.RelatedObjectDoesNotExist):
            return Response({'detail': 'Players have not been provided'}, status=406)
        match = Match(**data, red_score = 10, blue_score = 0)
        result2 = abs(match.calculate_points()[0])
        return Response({'blue': result1, 'red': result2})


class UserLatestMatchesView(APIView):
    def get(self, request, *args, **kwargs):
        user = Player.objects.get(username=kwargs['username'])
        num = request.GET.get('number', 7)

        serializer = MatchSerializer(instance=user.get_latest_matches(num), many=True)
        return Response(serializer.data)
