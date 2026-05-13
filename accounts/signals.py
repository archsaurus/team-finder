from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import generate_avatar
from .models import User


@receiver(post_save, sender=User)
def auto_generate_avatar(sender, instance, created, **kwargs):
    """Автоматически генерирует аватар для новых пользователей."""
    if created:
        generate_avatar(instance)
