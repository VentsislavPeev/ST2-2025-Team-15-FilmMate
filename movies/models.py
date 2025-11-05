from django.db import models
from django.utils import timezone
from django.conf import settings


class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    director = models.CharField(max_length=100)
    genres = models.ManyToManyField('genres.Genre', related_name='movie_genres')
    lists = models.ManyToManyField('lists.List', related_name='movie_lists')

    poster = models.URLField(max_length=255, blank=True, null=True)
    description = models.TextField()
    # Average rating computed from user reviews. Default 0.0 when no reviews.
    rating = models.FloatField(default=0.0)
    # Timestamp when rating was last recalculated
    rating_last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.year})"



class WatchedMovie(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watched_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by')
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"
