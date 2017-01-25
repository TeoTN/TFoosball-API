from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Player, ExpHistory, Match


@receiver(post_save, sender=Player)
def store_exp_history(sender, instance, *args, **kwargs):
    ExpHistory.objects.create(player=instance, exp=instance.exp)


@receiver(post_delete, sender=Match)
def clean_match(sender, instance, *args, **kwargs):
    has_blue_won = 1 if instance.blue_score > instance.red_score else -1
    instance.red_att.exp += has_blue_won*instance.points
    instance.red_def.exp += has_blue_won*instance.points
    instance.blue_att.exp -= has_blue_won*instance.points
    instance.blue_def.exp -= has_blue_won*instance.points
    instance.red_att.save()
    instance.red_def.save()
    instance.blue_att.save()
    instance.blue_def.save()
