import json, re

import ollama

from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from movies.models import WatchedMovie, Movie 
from genres.models import Genre
from lists.models import List
from reviews.forms import ReviewForm
from users.models import FriendRequest



def movie_home(request):
    """Homepage showing popular films and recent friend activity."""
    popular_films = Movie.objects.all()[7:14]
    friend_activities = []

    pending_requests = []
    if request.user.is_authenticated:
        # Friend requests
        pending_requests = (
            FriendRequest.objects.filter(to_user=request.user)
            .select_related('from_user')
            .order_by('-created')
        )

        # ✅ NEW FROM FRIENDS
        friends = request.user.friends.all()

        # Get up to 7 most recent movies watched by friends
        friend_activities = (
            WatchedMovie.objects.filter(user__in=friends)
            .select_related('user', 'movie')
            .order_by('-watched_at')[:7]
        )

    context = {
        'popular_films': popular_films,
        'friend_activities': friend_activities,
        'pending_requests': pending_requests,
    }
    return render(request, 'movies/home.html', context)

@login_required
def friends_activity(request):
    friends = request.user.friends.all()
    activities = (
        WatchedMovie.objects.filter(user__in=friends)
        .select_related('user', 'movie')
        .order_by('-watched_at')
    )
    paginator = Paginator(activities, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'movies/friends_activity.html', {'page_obj': page_obj})

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


def movie_detail(request, pk):
    """Show movie details + reviews + toggle watchlist + mark as watched + submit review."""
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.review_set.all().select_related("user").order_by("-date")

    # Get user's Watchlist (creates one if missing)
    watchlist, _ = List.objects.get_or_create(user=request.user, name="Watchlist")
    in_watchlist = movie in watchlist.movies.all()

    # Check if the movie is already watched
    watched = WatchedMovie.objects.filter(user=request.user, movie=movie).exists()

    form = ReviewForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        # Toggle Watchlist
        if action == 'toggle_watchlist':
            if in_watchlist:
                watchlist.movies.remove(movie)
            else:
                watchlist.movies.add(movie)
            return redirect('movies:movie_detail', pk=pk)

        # Mark as Watched (also remove from watchlist)
        elif action == 'mark_watched':
            WatchedMovie.objects.get_or_create(user=request.user, movie=movie)
            if in_watchlist:
                watchlist.movies.remove(movie)
            return redirect('movies:movie_detail', pk=pk)

        # Submit Review
        elif action == 'submit_review':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.movie = movie
                review.save()

                # Recalculate and update the movie's average rating
                avg_rating = movie.review_set.aggregate(Avg("rating"))["rating__avg"] or 0
                movie.rating = round(avg_rating, 1)
                movie.save(update_fields=["rating"])

                return redirect('movies:movie_detail', pk=pk)

    context = {
        'movie': movie,
        'reviews': reviews,
        'in_watchlist': in_watchlist,
        'watched': watched,
        'form': form,
    }
    return render(request, 'movies/movie_detail.html', context)



@login_required
def toggle_watched(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    watched_entry, created = WatchedMovie.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        watched_entry.delete()

    return redirect('movies:movie_detail', pk=movie_id)

@login_required
def my_films(request):
    """Display all movies the user has watched, with their ratings."""
    watched_movies = WatchedMovie.objects.filter(user=request.user).select_related("movie")
    reviews = {r.movie.id: r for r in request.user.review_set.all()}

    # Combine watched movies with rating info (if reviewed)
    watched_data = []
    for entry in watched_movies:
        movie = entry.movie
        review = reviews.get(movie.id)
        watched_data.append({
            "movie": movie,
            "rating": review.rating if review else None,
            "review_text": review.text if review else None,
        })

    context = {"watched_data": watched_data}
    return render(request, "movies/my_films.html", context)


def movies_all(request):
    query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    sort = request.GET.get('sort', 'title')

    movies = Movie.objects.all()

    # Search
    if query:
        movies = movies.filter(title__icontains=query)

    # Filter by genre
    if genre_filter:
        movies = movies.filter(genres__name__iexact=genre_filter).distinct()

    # Sorting
    if sort in ['title', 'year', 'director']:
        movies = movies.order_by(sort)

    # Pagination
    paginator = Paginator(movies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = Genre.objects.all()

    return render(request, 'movies/movies_all.html', {
        'page_obj': page_obj,
        'genres': genres,
        'query': query,
        'genre_filter': genre_filter,
        'sort': sort,
    })

def get_search_filters_from_ollama(message, genres_list):
    """
    Uses Ollama to parse a natural language message into a structured
    JSON object of search filters.
    """
    # Convert the list of genre names into a string for the prompt
    genres_str = ", ".join(genres_list)

    # This prompt is the most important part.
    # It instructs the LLM to act as a JSON-returning parser.
    system_prompt = f"""
    You are a movie database query assistant. Your job is to parse the user's
    message and extract search filters.
    
    You must ONLY respond with a single, valid JSON object.
    Do not add any explanation or preamble.
    
    The JSON object should have the following possible keys:
    - "genre": string (must be one of: {genres_str})
    - "director": string
    - "year": integer
    - "rating_gte": float (a number from 0-10, e.g., "8 stars" -> 8.0)
    - "keywords": string (for general title/description search)

    If you cannot find a value for a key, omit it or set it to null.
    If the message is just a greeting (like "hi" or "hello"), return an empty JSON object: {{}}
    
    Example user message: "show me some good sci-fi movies from the 90s"
    Example JSON response:
    {{"genre": "Sci-Fi", "year": 1990}}
    
    Example user message: "anything by Christopher Nolan with a 4-star rating"
    Example JSON response:
    {{"director": "Christopher Nolan", "rating_gte": 4.0}}
    
    Example user message: "a movie about space"
    Example JSON response:
    {{"keywords": "space"}}
    """

    try:
        response = ollama.chat(
            model='qwen3:4b',  # Your local model
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            options={
                'temperature': 0.0  # We want deterministic JSON, not creativity
            }
        )
        
        # Parse the LLM's JSON response
        llm_reply_content = response['message']['content']
        filters = json.loads(llm_reply_content)
        return filters

    except Exception as e:
        # If Ollama fails or returns bad JSON, fall back to simple keywords
        print(f"Ollama parsing failed: {e}")
        # Fallback: treat the whole message as keywords
        return {"keywords": message}
    
def generate_natural_reply(original_message, movies_list):
    """
    Uses Ollama to generate a conversational reply based on the 
    movies found in the database.
    """
    #
    if not movies_list:
        
        system_prompt = f"""
        You are FilmMate's assistant, a friendly and helpful movie expert.
        The user asked for a movie with: "{original_message}".
        
        Your database search found 0 results.
        
        Your task:
        Craft a brief, friendly reply (1-2 sentences) apologizing and 
        suggesting they try a different genre, director, or year.
        DO NOT output JSON. Just provide the conversational reply text.
        """
        
        user_content = "No movies found matching that query."
        
    else:  
        movies_json = json.dumps(movies_list, indent=2)
        
        system_prompt = f"""
        You are FilmMate's assistant, a friendly and helpful movie expert.
        Your job is to craft a brief, natural language reply based on movie results.
        
        The user originally asked: "{original_message}"
        
        Your database search found the following movies (in JSON format):
        {movies_json}
        
        Your task:
        1. Write a 1-2 sentence conversational reply.
        2. DO NOT just say "I found X movies".
        3. If there are multiple movies, *mention the first one by title*
           (e.g., "I found a few great options, including [Title]...")
        4. If there is only one, just mention it (e.g., "Yes! How about [Title]? It's...")
        5. Sound helpful and positive.
        6. DO NOT output JSON. Just provide the conversational reply text.
        """
        
        user_content = f"Found {len(movies_list)} movies. Please generate a reply."

    try:
        response = ollama.chat(
            model='qwen3:4b',  
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content}
            ],
            options={
                'temperature': 0.7  
            }
        )
        return response['message']['content'].strip()
    
    except Exception as e:
        print(f"Ollama reply generation failed: {e}")
        
        if movies_list:
            return f"I found {len(movies_list)} movie(s) matching your request. Here are the top results."
        else:
            return "Sorry, I couldn't find any movies matching that. Try a different genre, director or year."
        
@require_POST
def chat_api(request):
    """
    Hybrid chat endpoint. Uses Ollama to parse intent (Call 1) and 
    Django ORM to fetch. Then uses Ollama to generate a reply (Call 2).
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        message = payload.get('message', '').strip()
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    if not message:
        
        reply = "Hi — I'm FilmMate's assistant. Ask me for movie recommendations (genre, director, year, or keywords)."
        return JsonResponse({'reply': reply, 'movies': []})

    genres_list = list(Genre.objects.values_list('name', flat=True))
    filters = get_search_filters_from_ollama(message, genres_list)
    
    qs = Movie.objects.all()
    
    
    if filters.get('genre'):
        qs = qs.filter(genres__name__iexact=filters['genre']).distinct()
        
    
    qs = qs.order_by('-rating', '-year')[:12]

    movies_list = []
    for m in qs:
        detail_url = reverse('movies:movie_detail', args=[m.id])
        poster = m.poster if getattr(m, 'poster', None) else ''
        movies_list.append({
            'id': m.id,
            'title': m.title,
            'year': m.year,
            'director': m.director,
            'rating': float(m.rating) if m.rating is not None else 0.0,
            'detail_url': detail_url,
            'poster_url': poster,
        })

    reply = generate_natural_reply(message, movies_list)

    return JsonResponse({'reply': reply, 'movies': movies_list})