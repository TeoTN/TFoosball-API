import datetime

from django.test import TestCase

from .models import Player


class PlayerMethodTests(TestCase):
    def test_creating_player(self):
        player = Player(is_superuser=False, email='user@domain.com', last_name="Kowalski",
                        date_joined=datetime.datetime(2017, 1, 16), username='user', first_name='Jan', is_staff=False,
                        is_active=True, password='!CqPXpvVZ7hNREJMkm8GWWPEd088vLNY52C4KsiGl')
