from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path(
        'list/',
        views.UserListView.as_view(),
        name='user-list'
    ),
    path(
        '<int:pk>/',
        views.UserDetailView.as_view(),
        name='user-details'
    ),
    path(
        'login/',
        views.LoginView.as_view(),
        name='login'
    ),
    path(
        'logout/',
        views.LogoutView.as_view(),
        name='logout'
    ),
    path(
        'register/',
        views.RegisterView.as_view(),
        name='register'
    ),
    path(
        'change-password/',
        views.ChangePasswordView.as_view(),
        name='change-password'
    ),
    path(
        'edit-profile/',
        views.EditProfileView.as_view(),
        name='edit-profile'
    ),
]
