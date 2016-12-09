from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, ExpHistory


@receiver(post_save, sender=Player)
def store_exp_history(sender, instance, *args, **kwargs):
    ExpHistory.objects.create(player=instance, exp=instance.exp)
