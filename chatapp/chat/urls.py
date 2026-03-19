from django.urls import path
from .views import MessageListView, UserView, SignupView, LoginView

urlpatterns = [
    path('messages/<int:room_id>/', MessageListView.as_view(), name='message-list'),
    path('users', UserView.as_view(), name='list-users'),
    path('users/<int:user_id>/', UserView.as_view(), name='get-user'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
]
