# signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from decouple import config

@receiver(post_migrate)
def create_auth_user(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(username=config('DEFAULT_USER')).exists():
        User.objects.create_superuser(
            username=config('DEFAULT_USER'),
            email=config('DEFAULT_MAIL'),
            password=config('DEFAULT_PASS')
        )