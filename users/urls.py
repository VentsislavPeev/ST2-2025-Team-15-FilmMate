from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # friend requests
    path('friend-requests/', views.friend_requests_view, name='friend_requests'),
    path('friend-requests/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend-requests/send-by-username/', views.send_friend_request_by_username, name='send_friend_request_by_username'),
    path('friend-requests/accept/<int:fr_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-requests/decline/<int:fr_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friend-requests/cancel/<int:fr_id>/', views.cancel_friend_request, name='cancel_friend_request'),
]
