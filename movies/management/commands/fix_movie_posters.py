import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie 

class Command(BaseCommand):
    help = 'Fetches correct poster URLs for movies that have incorrect file paths.'

    def handle(self, *args, **options):
        self.stdout.write("Starting poster URL fix-up script...")

        # --- Define API configuration ---
        try:
            API_KEY = settings.TMDB_API_KEY
            IMAGE_BASE_URL = settings.TMDB_IMAGE_BASE
            DEFAULT_URL = getattr(settings, 'DEFAULT_POSTER_URL', None)
        except AttributeError as e:
            self.stdout.write(self.style.ERROR(
                f"Missing setting: {e}. Make sure TMDB_API_KEY and TMDB_IMAGE_BASE are in your settings.py"
            ))
            return

        SEARCH_URL = "https://api.themoviedb.org/3/search/movie"

        # Find all movies that have the "bad" URL format.
        # This assumes your old ImageField saved files to a directory named 'posters'.
        # Adjust 'posters/' if your 'upload_to' path was different.
        movies_to_fix = Movie.objects.filter(poster__startswith='posters/')
        
        if not movies_to_fix.exists():
            self.stdout.write(self.style.SUCCESS("No movies with bad poster paths found. Everything looks good!"))
            return

        self.stdout.write(f"Found {movies_to_fix.count()} movies to fix.")
        fixed_count = 0
        failed_count = 0

        for movie in movies_to_fix:
            self.stdout.write(f"--- Processing: {movie.title} ({movie.year}) ---")
            
            # 1. Search for the movie on TMDB
            params = {
                'api_key': API_KEY,
                'query': movie.title,
                'year': movie.year
            }
            
            try:
                response = requests.get(SEARCH_URL, params=params)
                response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
                data = response.json()

                if data.get('results'):
                    # 2. Found results, get the poster_path from the first one
                    first_result = data['results'][0]
                    poster_path = first_result.get('poster_path')

                    if poster_path:
                        # 3. We found a poster! Build the full URL and save it.
                        correct_url = f"{IMAGE_BASE_URL}{poster_path}"
                        movie.poster = correct_url
                        movie.save()
                        self.stdout.write(self.style.SUCCESS(f"  > SUCCESS: Updated poster for {movie.title}"))
                        fixed_count += 1
                    else:
                        # 4. Movie exists but has no poster. Save default.
                        self.stdout.write(self.style.WARNING(f"  > WARNING: No poster found on TMDB for {movie.title}."))
                        movie.poster = DEFAULT_URL
                        movie.save()
                        failed_count += 1
                else:
                    # 5. No results found for this movie. Save default.
                    self.stdout.write(self.style.ERROR(f"  > ERROR: Could not find {movie.title} on TMDB."))
                    movie.poster = DEFAULT_URL
                    movie.save()
                    failed_count += 1

            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"  > ERROR: API request failed for {movie.title}: {e}"))
                failed_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  > ERROR: A non-API error occurred for {movie.title}: {e}"))
                failed_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n--- Script Finished ---"))
        self.stdout.write(self.style.SUCCESS(f"Successfully fixed: {fixed_count}"))
        self.stdout.write(self.style.WARNING(f"Failed or no poster: {failed_count}"))
