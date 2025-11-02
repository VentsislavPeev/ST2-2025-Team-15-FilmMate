# movies/factories.py
from movies.models import Movie
from genres.models import Genre
from django.conf import settings

class MovieFactory:
    """
    Factory class for creating Movie objects from API data.
    Encapsulates creation logic so seeding and other modules can reuse it.
    """

    @staticmethod
    def create_movie(title, year, director, description, genre_ids, genre_list, poster_path=None):
        """Create and return a Movie instance with genres and poster URL."""

        # Skip duplicates
        if Movie.objects.filter(title=title, year=year).exists():
            return None  # skip duplicates gracefully

        # Determine final poster URL
        if poster_path:
            poster_url_to_save = f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            poster_url_to_save = getattr(settings, "DEFAULT_POSTER_URL", "")

        # Create movie instance
        movie = Movie.objects.create(
            title=title,
            year=year,
            director=director,
            description=description,
            poster=poster_url_to_save
        )

        # Assign genres from TMDb genre mapping
        genre_map = {g['id']: g['name'] for g in genre_list}
        for genre_id in genre_ids:
            name = genre_map.get(genre_id, 'Unknown')
            genre_obj, _ = Genre.objects.get_or_create(name=name)
            movie.genres.add(genre_obj)

        return movie
