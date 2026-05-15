from .models import CustomUser 
from .tasks import create_profile_task
from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import post_save

@receiver(post_save,sender=CustomUser)
def create_profile(sender,instance,created,**kwargs):
    if created:
        transaction.on_commit(
            lambda:create_profile_task.delay(instance.id)
        )