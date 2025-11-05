from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from movies.models import Movie
from genres.models import Genre
from lists.models import List
from django.contrib.auth.decorators import login_required
from reviews.forms import ReviewForm
from users.models import FriendRequest
from django.shortcuts import get_object_or_404, redirect
from movies.models import WatchedMovie 
from django.db.models import Avg



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
    """Show movie details + reviews + toggle watchlist + mark as watched + submit review."""
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.review_set.all().select_related("user").order_by("-date")

    # Get user's Watchlist (creates one if missing)
    watchlist, _ = List.objects.get_or_create(user=request.user, name="Watchlist")
    in_watchlist = movie in watchlist.movies.all()

    # Check if the movie is already watched
    watched = WatchedMovie.objects.filter(user=request.user, movie=movie).exists()

    form = ReviewForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        # Toggle Watchlist
        if action == 'toggle_watchlist':
            if in_watchlist:
                watchlist.movies.remove(movie)
            else:
                watchlist.movies.add(movie)
            return redirect('movies:movie_detail', pk=pk)

        # Mark as Watched (also remove from watchlist)
        elif action == 'mark_watched':
            WatchedMovie.objects.get_or_create(user=request.user, movie=movie)
            if in_watchlist:
                watchlist.movies.remove(movie)
            return redirect('movies:movie_detail', pk=pk)

        # Submit Review
        elif action == 'submit_review':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.movie = movie
                review.save()

                # Recalculate and update the movie's average rating
                avg_rating = movie.review_set.aggregate(Avg("rating"))["rating__avg"] or 0
                movie.rating = round(avg_rating, 1)
                movie.save(update_fields=["rating"])

                return redirect('movies:movie_detail', pk=pk)

    context = {
        'movie': movie,
        'reviews': reviews,
        'in_watchlist': in_watchlist,
        'watched': watched,
        'form': form,
    }
    return render(request, 'movies/movie_detail.html', context)



@login_required
def toggle_watched(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    watched_entry, created = WatchedMovie.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        watched_entry.delete()

    return redirect('movies:movie_detail', pk=movie_id)

@login_required
def my_films(request):
    """Display all movies the user has watched, with their ratings."""
    watched_movies = WatchedMovie.objects.filter(user=request.user).select_related("movie")
    reviews = {r.movie.id: r for r in request.user.review_set.all()}

    # Combine watched movies with rating info (if reviewed)
    watched_data = []
    for entry in watched_movies:
        movie = entry.movie
        review = reviews.get(movie.id)
        watched_data.append({
            "movie": movie,
            "rating": review.rating if review else None,
            "review_text": review.text if review else None,
        })

    context = {"watched_data": watched_data}
    return render(request, "movies/my_films.html", context)


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
    
    