from django.core.management.base import BaseCommand
from movies.models import Movie
from genres.models import Genre
import tmdbsimple as tmdb
import requests
from django.core.files.base import ContentFile
from django.conf import settings
import os

tmdb.API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'  # Base URL for poster images
DEFAULT_POSTER_PATH = os.path.join(settings.BASE_DIR, 'static', 'images', 'default-image.jpg')

class Command(BaseCommand):
    help = "Seed movies and genres from TMDb API with director and poster"

    def handle(self, *args, **options):
        # Get TMDb genre mapping once
        try:
            genre_list = tmdb.Genres().movie_list().get('genres', [])
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Failed to fetch genres: {e}"))
            genre_list = []

        # Fetch popular movies
        try:
            popular_movies = tmdb.Movies().popular().get('results', [])[:150]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch popular movies: {e}"))
            return

        for item in popular_movies:
            # Safe defaults
            title = item.get('title') or 'Untitled Movie'
            release_date = item.get('release_date') or ''
            year = int(release_date[:4]) if release_date else 0
            description = item.get('overview') or 'No description available'
            genre_ids = item.get('genre_ids', [])
            poster_path = item.get('poster_path')

            # ✅ Skip if movie already exists
            if Movie.objects.filter(title=title).exists():
                self.stdout.write(self.style.NOTICE(f"Movie '{title}' already exists. Skipping."))
                continue

            # Get director from credits
            director = 'Unknown'
            try:
                credits = tmdb.Movies(item['id']).credits()
                for member in credits.get('crew', []):
                    if member.get('job') == 'Director':
                        director = member.get('name') or 'Unknown'
                        break
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to fetch director for {title}: {e}"))

            # Create movie
            movie = Movie.objects.create(
                title=title,
                year=year,
                director=director,
                description=description,
            )

            # Add poster if available
            if poster_path:
                poster_url = f"{TMDB_IMAGE_BASE}{poster_path}"
                try:
                    response = requests.get(poster_url)
                    if response.status_code == 200:
                        movie.poster.save(
                            f"{title.replace(' ', '_')}.jpg",
                            ContentFile(response.content),
                            save=True
                        )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to download poster for {title}: {e}"))
            else:
                # Default poster fallback
                if os.path.exists(DEFAULT_POSTER_PATH):
                    with open(DEFAULT_POSTER_PATH, 'rb') as f:
                        movie.poster.save(
                            f"default_{title.replace(' ', '_')}.jpg",
                            ContentFile(f.read()),
                            save=True
                        )

            # Add genres
            for genre_id in genre_ids:
                name = next((g['name'] for g in genre_list if g['id'] == genre_id), None) or 'Unknown'
                genre_obj, _ = Genre.objects.get_or_create(name=name)
                movie.genres.add(genre_obj)

            self.stdout.write(self.style.SUCCESS(f"Movie '{movie.title}' added."))
