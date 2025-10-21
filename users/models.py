from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    # Mutual friendships between users. blank=True allows no friends.
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='friends_rel',
        help_text='Users you are friends with'
    )
    

    def __str__(self):
        return self.username