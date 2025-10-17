from django.shortcuts import render
from .models import Movie

def movie_home(request):
    popular_films = Movie.objects.all()[:20] 
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