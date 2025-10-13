from django.db import models
from django.conf import settings


class Genre(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    movies = models.ManyToManyField('movies.Movie', related_name='genres_movies')

    def __str__(self):
        return f"{self.name}"
