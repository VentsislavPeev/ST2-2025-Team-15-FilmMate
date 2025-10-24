from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.movie_home, name='home'),      
    path('list/', views.movie_list, name='movie_list'), 
    path('search/', views.movie_search, name='movie_search'), 
    path('<int:pk>/', views.movie_detail, name='movie_detail'),
    path('all/', views.movies_all, name='movies_all'),
]
