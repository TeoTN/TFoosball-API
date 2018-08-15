from random import randint
from tfoosball.models import Member


def generate_username(team, email):
    if not email or not team:
        return ''
    unique = False
    username = ''
    while not unique:
        core = email.rsplit('@')[0]
        username = f'{core}-{randint(1000, 9999)}'[:32]
        unique = not Member.objects.filter(team=team, username=username).exists()
    return username
