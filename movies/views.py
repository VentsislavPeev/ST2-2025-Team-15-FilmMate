from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from movies.models import Movie
from genres.models import Genre
from lists.models import List
from django.contrib.auth.decorators import login_required
from users.models import FriendRequest


def movie_home(request):
    popular_films = Movie.objects.all()[7:14]
    friend_activities = []

    pending_requests = []
    if request.user.is_authenticated:
        pending_requests = (
            FriendRequest.objects.filter(to_user=request.user)
            .select_related('from_user')
            .order_by('-created')
        )

    context = {
        'popular_films': popular_films,
        'friend_activities': friend_activities,
        'pending_requests': pending_requests,
    }
    return render(request, 'movies/home.html', context)


def movie_list(request):
    movies = Movie.objects.all()
    context = {
        'movies': movies,
    }
    return render(request, 'movies/list.html', context)

def movie_search(request):
    query = request.GET.get('q', '').strip()
    if query:
        results = Movie.objects.filter(title__icontains=query)
    else:
        results = Movie.objects.none() 

    friend_activities = []

    context = {
        'popular_films': results,
        'friend_activities': friend_activities,
        'query': query,
    }
    return render(request, 'movies/home.html', context)

def movie_detail(request, pk):
    """Show movie details + reviews + toggle watchlist with a single button."""
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.review_set.all().order_by('-date')

    # Get or create the user's Watchlist
    watchlist, _ = List.objects.get_or_create(user=request.user, name="Watchlist")

    # Check if the movie is currently in the watchlist
    in_watchlist = movie in watchlist.movies.all()

    if request.method == 'POST':
        # Toggle the movie in the watchlist
        if in_watchlist:
            watchlist.movies.remove(movie)
        else:
            watchlist.movies.add(movie)
        return redirect('movies:movie_detail', pk=pk)  # Reload page to update button

    context = {
        'movie': movie,
        'reviews': reviews,
        'in_watchlist': in_watchlist,
    }
    return render(request, 'movies/movie_detail.html', context)

def movies_all(request):
    query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    sort = request.GET.get('sort', 'title')

    movies = Movie.objects.all()

    # Search
    if query:
        movies = movies.filter(title__icontains=query)

    # Filter by genre
    if genre_filter:
        movies = movies.filter(genres__name__iexact=genre_filter).distinct()

    # Sorting
    if sort in ['title', 'year', 'director']:
        movies = movies.order_by(sort)

    # Pagination
    paginator = Paginator(movies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = Genre.objects.all()

    return render(request, 'movies/movies_all.html', {
        'page_obj': page_obj,
        'genres': genres,
        'query': query,
        'genre_filter': genre_filter,
        'sort': sort,
    })