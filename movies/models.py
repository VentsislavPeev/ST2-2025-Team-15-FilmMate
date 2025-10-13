from django.db import models
from genres.models import Genre

class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    genres = models.ManyToManyField(Genre,related_name='genres')
    director = models.CharField(max_length=100)
    poster = models.ImageField(upload_to='posters/')
    description = models.TextField()

    def __str__(self):
        return f"{self.title} ({self.year})"
