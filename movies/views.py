from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from movies.models import Movie
from genres.models import Genre
from lists.models import List
from django.contrib.auth.decorators import login_required
from users.models import FriendRequest
from django.shortcuts import get_object_or_404, redirect
from movies.models import WatchedMovie 


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

@login_required
def movie_detail(request, pk):
    """Show movie details + reviews + toggle watchlist + mark as watched."""
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.review_set.all().order_by('-date') if hasattr(movie, 'review_set') else []

    # Get or create Watchlist
    watchlist, _ = List.objects.get_or_create(user=request.user, name="Watchlist")
    in_watchlist = movie in watchlist.movies.all()

    # Check if movie is already watched
    watched = WatchedMovie.objects.filter(user=request.user, movie=movie).exists()

    if request.method == 'POST':
        action = request.POST.get('action')

        # ✅ Handle "Add/Remove from Watchlist"
        if action == 'toggle_watchlist':
            if in_watchlist:
                watchlist.movies.remove(movie)
            else:
                watchlist.movies.add(movie)

        # ✅ Handle "Mark as Watched"
        elif action == 'mark_watched':
            WatchedMovie.objects.get_or_create(user=request.user, movie=movie)
            if in_watchlist:
                watchlist.movies.remove(movie)  # ❌ Remove from watchlist if watched

        return redirect('movies:movie_detail', pk=pk)

    context = {
        'movie': movie,
        'reviews': reviews,
        'in_watchlist': in_watchlist,
        'watched': watched,
    }
    return render(request, 'movies/movie_detail.html', context)



@login_required
def toggle_watched(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    watched_entry, created = WatchedMovie.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        watched_entry.delete()

    return redirect('movies:movie_detail', pk=movie_id)

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