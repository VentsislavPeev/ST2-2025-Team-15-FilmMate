from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import CustomUser  # ✅ Import this for user lookups
from .models import List
from movies.models import Movie

@login_required
def list_overview(request):
    """Show all lists created by the user."""
    lists = List.objects.filter(user=request.user)
    return render(request, 'lists/list_overview.html', {'lists': lists})

@login_required
def list_create(request):
    """Create a new list and optionally add movies."""
    movies = Movie.objects.all()
    error_message = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        movie_ids = request.POST.getlist('movies')

        if not name:
            error_message = "List name cannot be empty."
        elif List.objects.filter(user=request.user, name__iexact=name).exists():
            error_message = "You already have a list with this name."

        if not error_message:
            new_list = List.objects.create(
                user=request.user,
                name=name,
                description=description
            )
            new_list.movies.set(movie_ids)
            return redirect('lists:list_overview')

    return render(request, 'lists/list_create.html', {
        'movies': movies,
        'error_message': error_message,
    })

@login_required
def list_detail(request, pk):
    """Show details of a specific list."""
    user_list = get_object_or_404(List, pk=pk, user=request.user)
    return render(request, 'lists/list_detail.html', {'list': user_list})

@login_required
def list_edit(request, pk):
    """Edit an existing list (name, description, movies)."""
    user_list = get_object_or_404(List, pk=pk, user=request.user)
    movies = Movie.objects.all()
    error_message = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        selected_movie_ids = request.POST.getlist('movies')

        if not name:
            error_message = "List name cannot be empty."
        elif List.objects.filter(user=request.user, name__iexact=name).exclude(pk=user_list.pk).exists():
            error_message = "You already have another list with this name."

        if not error_message:
            user_list.name = name
            user_list.description = description
            user_list.movies.set(selected_movie_ids)
            user_list.save()
            return redirect('lists:list_detail', pk=pk)

    return render(request, 'lists/list_edit.html', {
        'list': user_list,
        'movies': movies,
        'error_message': error_message,
    })

@login_required
def list_delete(request, pk):
    """Delete a user list."""
    user_list = get_object_or_404(List, pk=pk, user=request.user)
    if request.method == 'POST':
        user_list.delete()
        return redirect('lists:list_overview')
    return render(request, 'lists/list_confirm_delete.html', {'list': user_list})

@login_required
def remove_movie(request, list_id, movie_id):
    """Remove a movie from a list."""
    user_list = get_object_or_404(List, pk=list_id, user=request.user)
    movie = get_object_or_404(Movie, pk=movie_id)
    user_list.movies.remove(movie)
    return redirect('lists:list_detail', pk=list_id)

@login_required
def add_to_watchlist(request, movie_id):
    """Add a movie to the user's Watchlist (create it if it doesn't exist)."""
    movie = get_object_or_404(Movie, pk=movie_id)
    watchlist, created = List.objects.get_or_create(user=request.user, name="Watchlist")
    watchlist.movies.add(movie)
    return redirect('movies:movie_detail', pk=movie.id)

# ✅ NEW VIEW: Watchlist Page
@login_required
def watchlist_view(request, user_id=None):
    """Display the full watchlist for a user."""
    if user_id is None:
        user = request.user
    else:
        user = get_object_or_404(CustomUser, pk=user_id)

    watchlist = List.objects.filter(user=user, name__icontains="watchlist").first()
    watchlist_movies = watchlist.movies.all() if watchlist else []
    is_own_profile = (user == request.user)

    context = {
        'watchlist_owner': user,
        'watchlist_movies': watchlist_movies,
        'is_own_profile': is_own_profile,
    }
    return render(request, 'lists/watchlist_page.html', context)
