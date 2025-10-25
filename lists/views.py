from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import List
from movies.models import Movie

@login_required
def list_overview(request):
    lists = List.objects.filter(user=request.user)
    return render(request, 'lists/list_overview.html', {'lists': lists})

@login_required
def list_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        movie_ids = request.POST.getlist('movies')

        new_list = List.objects.create(
            user=request.user,
            name=name,
            description=description
        )
        new_list.movies.set(movie_ids)
        return redirect('lists:list_overview')

    movies = Movie.objects.all()[:20]
    return render(request, 'lists/list_create.html', {'movies': movies})


@login_required
def list_detail(request, pk):
    user_list = get_object_or_404(List, pk=pk, user=request.user)
    return render(request, 'lists/list_detail.html', {'list': user_list})

@login_required
def list_delete(request, pk):
    user_list = get_object_or_404(List, pk=pk, user=request.user)
    if request.method == 'POST':
        user_list.delete()
        return redirect('lists:list_overview')
    return render(request, 'lists/list_confirm_delete.html', {'list': user_list})

@login_required
def remove_movie(request, list_id, movie_id):
    user_list = get_object_or_404(List, pk=list_id, user=request.user)
    movie = get_object_or_404(Movie, pk=movie_id)
    user_list.movies.remove(movie)
    return redirect('lists:list_detail', pk=list_id)

@login_required
def list_edit(request, pk):
    user_list = get_object_or_404(List, pk=pk, user=request.user)
    movies = Movie.objects.all()

    if request.method == 'POST':
        user_list.name = request.POST.get('name')
        user_list.description = request.POST.get('description')
        selected_movie_ids = request.POST.getlist('movies')
        user_list.movies.set(selected_movie_ids)
        user_list.save()
        return redirect('lists:list_detail', pk=pk)

    context = {
        'list': user_list,
        'movies': movies,
    }
    return render(request, 'lists/list_edit.html', context)

