from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from users.forms import CustomUserCreationForm, CustomAuthenticationForm
from users.models import FriendRequest, CustomUser
from filmmate.settings import LOGIN_REDIRECT_URL
from movies.models import Movie
from reviews.models import Review
from lists.models import List

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(LOGIN_REDIRECT_URL)  # Change to your homepage
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(LOGIN_REDIRECT_URL)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def friend_requests_view(request):
    """Show incoming and outgoing friend requests for the current user."""
    incoming = FriendRequest.objects.filter(to_user=request.user).select_related('from_user')
    outgoing = FriendRequest.objects.filter(from_user=request.user).select_related('to_user')
    return render(request, 'users/friend_requests.html', {'incoming': incoming, 'outgoing': outgoing})

@login_required
@require_POST
def send_friend_request(request, user_id):
    """Send a friend request from request.user to user_id."""
    if request.user.id == int(user_id):
        return HttpResponseForbidden("Cannot friend yourself")
    
    to_user = get_object_or_404(CustomUser, pk=user_id)
    
    # prevent duplicate requests or if already friends
    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists() or request.user.friends.filter(pk=to_user.pk).exists():
        messages.info(request, 'Friend request already sent or you are already friends.')
        # Redirect back to the user's profile instead of general friend requests page
        return redirect('users:profile_other', user_id=to_user.id)
    
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, 'Friend request sent.')
    return redirect('users:profile_other', user_id=to_user.id)

@login_required
@require_POST
def send_friend_request_by_username(request):
    """Send a friend request by posting a username in a form field named 'username'."""
    username = request.POST.get('username', '').strip()
    if not username:
        messages.error(request, 'Please provide a username.')
        return redirect(reverse('users:friend_requests'))

    try:
        to_user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect(reverse('users:friend_requests'))

    if to_user == request.user:
        messages.error(request, "You can't friend yourself.")
        return redirect(reverse('users:friend_requests'))

    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists() or request.user.friends.filter(pk=to_user.pk).exists():
        messages.info(request, 'Friend request already sent or you are already friends.')
        return redirect(reverse('users:friend_requests'))

    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, f'Friend request sent to {to_user.username}.')
    return redirect(reverse('users:friend_requests'))

@login_required
@require_POST
def accept_friend_request(request, fr_id):
    fr = get_object_or_404(FriendRequest, pk=fr_id, to_user=request.user)
    # add each other as friends
    fr.to_user.friends.add(fr.from_user)
    fr.from_user.friends.add(fr.to_user)
    fr.delete()
    messages.success(request, 'Friend request accepted.')
    return redirect(reverse('users:friend_requests'))

@login_required
@require_POST
def decline_friend_request(request, fr_id):
    fr = get_object_or_404(FriendRequest, pk=fr_id, to_user=request.user)
    fr.delete()
    messages.info(request, 'Friend request declined.')
    return redirect(reverse('users:friend_requests'))

@login_required
@require_POST
def cancel_friend_request(request, fr_id):
    fr = get_object_or_404(FriendRequest, pk=fr_id, from_user=request.user)
    fr.delete()
    messages.info(request, 'Friend request cancelled.')
    return redirect(reverse('users:friend_requests'))

@login_required
@require_POST
def remove_friend(request, user_id):
    """Remove a friend relationship between the current user and another user."""
    if request.user.id == int(user_id):
        messages.error(request, "You cannot remove yourself.")
        return redirect('users:profile', user_id=request.user.id)

    friend_user = get_object_or_404(CustomUser, pk=user_id)

    if not request.user.friends.filter(pk=friend_user.pk).exists():
        messages.info(request, f"{friend_user.username} is not in your friends list.")
        return redirect('users:profile_other', user_id=friend_user.id)

    # Remove each other from friends
    request.user.friends.remove(friend_user)
    friend_user.friends.remove(request.user)

    messages.success(request, f"You are no longer friends with {friend_user.username}.")
    return redirect('users:profile_other', user_id=friend_user.id)

@require_POST
def logout_view(request):
    logout(request)
    return redirect(LOGIN_REDIRECT_URL)

@login_required
def profile_view(request, user_id=None):
    """Show either the logged-in user's profile or another user's profile."""
    # If no user_id, show the current user's profile
    if user_id is None:
        profile_user = request.user
    else:
        profile_user = get_object_or_404(CustomUser, pk=user_id)

    # Shared data
    reviews = Review.objects.filter(user=profile_user).select_related('movie')[:4]
    watchlist = List.objects.filter(user=profile_user, name__icontains="watchlist").first()
    watchlist_movies = watchlist.movies.all()[:4] if watchlist else []
    friends = profile_user.friends.all()

    all_reviews_count = Review.objects.filter(user=profile_user).count()
    seen_movies_count = Review.objects.filter(user=profile_user).values_list('movie', flat=True).distinct().count()

    # Check if this is the current user's own profile
    is_own_profile = (profile_user == request.user)

    # Check if already friends (for showing Add/Remove Friend button later)
    is_friend = request.user.friends.filter(pk=profile_user.pk).exists() if not is_own_profile else False

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'is_friend': is_friend,
        'recent_reviews': reviews,
        'recent_watchlist_movies': watchlist_movies,
        'friends': friends,
        'seen_movies_count': seen_movies_count,
        'all_reviews_count': all_reviews_count,
    }
    return render(request, 'users/profile.html', context)
