from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Match, Player, PlayerPlaceholder, Member
from allauth.account.signals import user_signed_up
from django.utils import timezone


@receiver(post_save, sender=Match)
def store_exp_history(sender, instance, *args, **kwargs):
    Match.create_exp_history(instance)


@receiver(pre_save, sender=Member)
def set_date_joined(sender, instance, *args, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if not obj.is_accepted == instance.is_accepted and instance.is_accepted:
            instance.joined_date = timezone.now()


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


@receiver(user_signed_up, sender=Player)
def user_created(request, user, *args, **kwargs):
    placeholders = PlayerPlaceholder.objects.filter(email=user.email)
    for placeholder in placeholders:
        placeholder.member.player = user
        placeholder.member.save()
        placeholder.delete()
