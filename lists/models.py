from django.db import models
from django.conf import settings
from movies.models import Movie

class List(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    movies = models.ManyToManyField('movies.Movie', related_name='lists_movies')

    def __str__(self):
        return f"{self.name} by {self.user.username}"
