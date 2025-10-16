from django.urls import path
from . import views
from django.http import HttpResponse

def movie_list(request):
    return HttpResponse("Movie list placeholder")

app_name = 'movies'
urlpatterns = [
    path('', views.movie_list, name='home'),  
]
