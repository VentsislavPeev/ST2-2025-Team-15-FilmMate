from django.core.management.base import BaseCommand
from django.db.models import Avg
from django.utils import timezone

from movies.models import Movie
from reviews.models import Review


class Command(BaseCommand):
    help = 'Recalculate average movie ratings from user reviews and store in Movie.rating'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        total = movies.count()
        self.stdout.write(f'Recalculating ratings for {total} movies...')
        for i, movie in enumerate(movies, start=1):
            agg = Review.objects.filter(movie=movie).aggregate(avg_rating=Avg('rating'))
            avg = agg['avg_rating']
            if avg is None:
                movie.rating = 0.0
            else:
                # keep average on same 1-10 scale as Review
                movie.rating = float(avg)
            movie.rating_last_updated = timezone.now()
            movie.save(update_fields=['rating', 'rating_last_updated'])
            self.stdout.write(f'[{i}/{total}] {movie.title}: {movie.rating}')
        self.stdout.write('Done.')
