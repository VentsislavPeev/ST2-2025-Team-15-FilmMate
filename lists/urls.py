from django.urls import path
from . import views

app_name = 'lists'

urlpatterns = [
    path('', views.list_overview, name='list_overview'),
    path('create/', views.list_create, name='list_create'),
    path('<int:pk>/', views.list_detail, name='list_detail'),
    path('<int:pk>/edit/', views.list_edit, name='list_edit'),
    path('<int:pk>/delete/', views.list_delete, name='list_delete'),
    path('<int:list_id>/remove-movie/<int:movie_id>/', views.remove_movie, name='remove_movie'),
    path('add-to-watchlist/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),

    # ✅ NEW: full watchlist page (works for your profile link)
    path('watchlist/<int:user_id>/', views.watchlist_view, name='watchlist_page'),
]
