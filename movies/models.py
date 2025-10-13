from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    director = models.CharField(max_length=100)
    genres = models.ManyToManyField('genres.Genre', related_name='movie_genres')
    lists = models.ManyToManyField('lists.List', related_name='movie_lists')

    poster = models.ImageField(upload_to='posters/')
    description = models.TextField()

    def __str__(self):
        return f"{self.title} ({self.year})"
