import json
from django.db.models.signals import post_save, post_delete
from django.forms.models import model_to_dict
from django.dispatch import receiver
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from .models import Player, ExpHistory
from .serializers import UserSerializer


@receiver(post_save, sender=Player)
def store_exp_history(sender, instance, *args, **kwargs):
    ExpHistory.objects.create(player=instance, exp=instance.exp)


@receiver(post_save, sender=Player)
def broadcast_update(sender, instance, created, update_fields, *args, **kwargs):
    redis_publisher = RedisPublisher(facility='users', broadcast=True)
    fields = UserSerializer().fields
    if not created and update_fields is not None:
        fields = list(filter(lambda f: f in fields, update_fields))
        if len(fields) == 0:
            return
    data = {
        'type': 'USER::ADD' if created else 'USER::UPDATE',
        'userData': model_to_dict(instance, fields=fields),
        'id': instance.id,
    }
    message = RedisMessage(json.dumps(data))
    redis_publisher.publish_message(message)


@receiver(post_delete, sender=Player)
def broadcast_delete(sender, instance, *args, **kwargs):
    redis_publisher = RedisPublisher(facility='users', broadcast=True)
    data = {
        'type': 'USER::DELETE',
        'id': instance.id,
    }
    message = RedisMessage(json.dumps(data))
    redis_publisher.publish_message(message)
