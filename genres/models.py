from django.db import models
from django.conf import settings
from movies.models import Movie

class Genre(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    movies = models.ManyToManyField(Movie, related_name='genres')

    def __str__(self):
        return f"{self.name}"
