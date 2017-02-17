from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Match, ExpHistory


@receiver(post_save, sender=Match)
def store_exp_history(sender, instance, *args, **kwargs):
    ExpHistory.objects.create(player=instance.red_att, exp=instance.red_att.exp, match=instance)
    ExpHistory.objects.create(player=instance.red_def, exp=instance.red_def.exp, match=instance)
    ExpHistory.objects.create(player=instance.blue_def, exp=instance.blue_def.exp, match=instance)
    ExpHistory.objects.create(player=instance.blue_att, exp=instance.blue_att.exp, match=instance)


@receiver(post_delete, sender=Match)
def clean_match(sender, instance, *args, **kwargs):
    instance.red_att.exp -= instance.points
    instance.red_def.exp -= instance.points
    instance.blue_att.exp += instance.points
    instance.blue_def.exp += instance.points
    instance.red_att.save()
    instance.red_def.save()
    instance.blue_att.save()
    instance.blue_def.save()
