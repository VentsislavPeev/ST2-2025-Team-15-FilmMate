from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    genre = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    poster = models.ImageField(upload_to='posters/')
    description = models.TextField()

    def __str__(self):
        return f"{self.title} ({self.year})"
