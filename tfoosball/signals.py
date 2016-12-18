from django.db.models.signals import post_save
from django.dispatch import receiver
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from .models import Player, ExpHistory


@receiver(post_save, sender=Player)
def store_exp_history(sender, instance, *args, **kwargs):
    ExpHistory.objects.create(player=instance, exp=instance.exp)


@receiver(post_save, sender=Player)
def broadcast_update(sender, instance, *args, **kwargs):
    redis_publisher = RedisPublisher(facility='tfoosball.user.update', broadcast=True)
    message = RedisMessage(instance.model_to_dict())
    redis_publisher.publish_message(message)
