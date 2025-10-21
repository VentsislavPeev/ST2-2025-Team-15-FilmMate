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


class FriendRequest(models.Model):
    """A simple friend request from one user to another."""
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='unique_friend_request')
        ]

    def __str__(self):
        return f"FriendRequest(from={self.from_user_id}, to={self.to_user_id})"