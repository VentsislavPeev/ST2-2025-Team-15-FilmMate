from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie

def movie_list(request):
    return HttpResponse("This will be the list of movies.")

def movie_list(request):
    # Get all movies from the database (you can later add filters like "popular")
    popular_films = Movie.objects.all()

    # Placeholder for friend activities (you can integrate real data later)
    friend_activities = []

    # Send data to the template
    context = {
        'popular_films': popular_films,
        'friend_activities': friend_activities,
    }
    return render(request, 'movies/home.html', context)

#search functionality
def movie_list(request):
    query = request.GET.get('q')
    if query:
        popular_films = Movie.objects.filter(title__icontains=query)
    else:
        popular_films = Movie.objects.all()

    friend_activities = []

    context = {
        'popular_films': popular_films,
        'friend_activities': friend_activities,
    }
    return render(request, 'movies/home.html', context)

