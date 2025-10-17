from django.http import HttpResponse
from django.shortcuts import render
from .models import Movie

def movie_list(request):
    return HttpResponse("This will be the list of movies.")


def movie_home(request):
    popular_films = Movie.objects.all()

    friend_activities = []

    context = {
        'popular_films': popular_films,
        'friend_activities': friend_activities,
    }

    return render(request, 'movies/home.html', context)


def movie_search(request):
    query = request.GET.get('q')

    if query:
        popular_films = Movie.objects.filter(title__icontains=query)
    else:
        popular_films = Movie.objects.all()

    friend_activities = []

    context = {
        'popular_films': popular_films,
        'friend_activities': friend_activities,
        'query': query, 
    }

    return render(request, 'movies/home.html', context)
