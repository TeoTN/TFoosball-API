import datetime

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from tfoosball.views import MatchViewSet
from .models import Player


class PlayerMethodTests(TestCase):
    def test_creating_player(self):
        player = Player(is_superuser=False, email='user@domain.com', last_name="Kowalski",
                        date_joined=datetime.datetime(2017, 1, 16), username='user', first_name='Jan', is_staff=False,
                        is_active=True, password='!CqPXpvVZ7hNREJMkm8GWWPEd088vLNY52C4KsiGl')
        player.save()


class APITests(TestCase):
    def test_add_match(self):
        player1 = Player(is_superuser=False, email='user@domain.com', last_name="Kowalski",
                        date_joined=datetime.datetime(2017, 1, 16), username='user1', first_name='Jan', is_staff=False,
                        is_active=True, password='!CqPXpvVZ7hNREJMkm8GWWPEd088vLNY52C4KsiGl')
        player2 = Player(is_superuser=False, email='user@domain.com', last_name="Kowalski",
                        date_joined=datetime.datetime(2017, 1, 16), username='user2', first_name='Jan', is_staff=False,
                        is_active=True, password='!CqPXpvVZ7hNREJMkm8GWWPEd088vLNY52C4KsiGl')
        player3 = Player(is_superuser=False, email='user@domain.com', last_name="Kowalski",
                        date_joined=datetime.datetime(2017, 1, 16), username='user3', first_name='Jan', is_staff=False,
                        is_active=True, password='!CqPXpvVZ7hNREJMkm8GWWPEd088vLNY52C4KsiGl')
        player4 = Player(is_superuser=False, email='user@domain.com', last_name="Kowalski",
                        date_joined=datetime.datetime(2017, 1, 16), username='user4', first_name='Jan', is_staff=False,
                        is_active=True, password='!CqPXpvVZ7hNREJMkm8GWWPEd088vLNY52C4KsiGl')

        player1.save()
        player2.save()
        player3.save()
        player4.save()

        factory = APIRequestFactory()
        request = factory.post('/matches/', {
            'red_att': player1.username,
            'red_def': player2.username,
            'blue_att': player3.username,
            'blue_def': player4.username,
            'red_score': 10,
            'blue_score': 1
        })
        request.user = player1

        view = MatchViewSet.as_view({"post": "create"})
        response = view(request)
        self.assertEqual(response.status_code, 201)
