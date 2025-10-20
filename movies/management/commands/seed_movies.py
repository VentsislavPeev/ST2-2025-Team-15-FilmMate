from django.core.management.base import BaseCommand
from movies.models import Movie
from genres.models import Genre
import tmdbsimple as tmdb
import requests
from django.core.files.base import ContentFile

tmdb.API_KEY = 'b85cd30c758ab8c37eaec969e07e1b53'  
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'  # Base URL for poster images

class Command(BaseCommand):
    help = "Seed movies and genres from TMDb API with director and poster"

    def handle(self, *args, **options):
        # Get TMDb genre mapping once
        genre_list = tmdb.Genres().movie_list()['genres']

        # Fetch popular movies
        popular_movies = tmdb.Movies().popular()['results'][:10]  # limit to first 10

        for item in popular_movies:
            title = item.get('title')
            release_date = item.get('release_date')
            year = int(release_date[:4]) if release_date else 0
            description = item.get('overview', '')
            genre_ids = item.get('genre_ids', [])
            poster_path = item.get('poster_path')

            # Get director from credits
            credits = tmdb.Movies(item['id']).credits()
            director = 'Unknown'
            for member in credits.get('crew', []):
                if member.get('job') == 'Director':
                    director = member.get('name')
                    break

            # Create or get movie
            movie, created = Movie.objects.get_or_create(
                title=title,
                defaults={
                    'year': year,
                    'director': director,
                    'description': description,
                }
            )

            # Add poster if available
            if poster_path:
                poster_url = f"{TMDB_IMAGE_BASE}{poster_path}"
                response = requests.get(poster_url)
                if response.status_code == 200:
                    # Save poster to ImageField
                    movie.poster.save(
                        f"{title.replace(' ', '_')}.jpg",
                        ContentFile(response.content),
                        save=True
                    )

            # Add genres
            for genre_id in genre_ids:
                name = next((g['name'] for g in genre_list if g['id'] == genre_id), None)
                if name:
                    genre_obj, _ = Genre.objects.get_or_create(name=name)
                    movie.genres.add(genre_obj)

            self.stdout.write(self.style.SUCCESS(f"Movie '{movie.title}' added/updated."))
