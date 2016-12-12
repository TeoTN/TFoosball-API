from django.core.management.base import BaseCommand
from tfoosball.models import Player, Match
from random import shuffle, randint
import json

class Command(BaseCommand):
	help = 'Populates db with randomly generated matches. Requires at least 4 users in db.'

	def create_matches(self, number):
		users = list(Player.objects.all())
		if len(users) < 4:
			raise ValueError("Not enough players")
		for _ in range(number):
			shuffle(users)
			red_score = randint(0, 10)
			blue_score = 10 if red_score != 10 else randint(0, 10)
			Match.objects.create(
				red_att=users[0],
				red_def=users[1],
				blue_att=users[2],
				blue_def=users[3],
				red_score=red_score,
				blue_score=blue_score
				)

	def add_arguments(self, parser):
		parser.add_argument(
			'--number',
			dest='number',
			default='10'
			)

	def handle(self, *args, **options):
		self.create_matches(options['number'])
