# movies/views.py
from django.shortcuts import render

def home_view(request):
    # fake data for now
    movies = [
        {"title": "Inception", "year": 2010, "genre": "Sci-Fi"},
        {"title": "Interstellar", "year": 2014, "genre": "Adventure"},
    ]
    return render(request, "movies/home.html", {"movies": movies})
