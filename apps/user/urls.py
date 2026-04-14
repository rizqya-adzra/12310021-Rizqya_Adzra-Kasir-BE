from django.urls import path
from apps.user.views.authentications import LoginView, LogoutView
from apps.user.views.profiles import MyProfileView, UserDetailView, UserListCreateView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('profile/', MyProfileView.as_view(), name='my-profile'),

    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<str:email>/', UserDetailView.as_view(), name='user-detail'),
]