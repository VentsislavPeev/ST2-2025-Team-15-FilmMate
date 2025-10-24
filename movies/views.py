from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from movies.models import Movie
from genres.models import Genre


def movie_home(request):
    popular_films = Movie.objects.all()[7:14] 
    friend_activities = [] 

    context = {
        'popular_films': popular_films,
        'friend_activities': friend_activities,
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
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'movies/movie_detail.html', {'movie': movie})

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
        movies = movies.filter(genres__name__iexact=genre_filter)

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