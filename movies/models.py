from django.db import models
from django.utils import timezone

class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    director = models.CharField(max_length=100)
    genres = models.ManyToManyField('genres.Genre', related_name='movie_genres')
    lists = models.ManyToManyField('lists.List', related_name='movie_lists')

    poster = models.ImageField(upload_to='posters/')
    description = models.TextField()
    # Average rating computed from user reviews. Default 0.0 when no reviews.
    rating = models.FloatField(default=0.0)
    # Timestamp when rating was last recalculated
    rating_last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.year})"
