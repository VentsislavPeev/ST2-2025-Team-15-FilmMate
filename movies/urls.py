from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.movie_home, name='home'),      
    path('list/', views.movie_list, name='movie_list'), 
    path('search/', views.movie_search, name='movie_search'), 
]
