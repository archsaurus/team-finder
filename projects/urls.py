from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path(
        'list/',
        views.ProjectListView.as_view(),
        name='project-list'
    ),
    path(
        '<int:pk>/',
        views.ProjectDetailView.as_view(),
        name='project-detail'
    ),
    path(
        '<int:pk>/toggle-favorite/',
        views.ToggleFavoriteAPIView.as_view(),
        name='toggle-favorite'
    ),
    path(
        'favorites/',
        views.FavoriteProjectListView.as_view(),
        name='favorite-projects'
    ),
    path(
        '<int:pk>/edit/',
        views.ProjectUpdateView.as_view(),
        name='project-edit'
    ),
    path(
        'create-project/',
        views.ProjectCreateView.as_view(),
        name='project-create'
    ),
    path(
        '<int:pk>/complete/',
        views.ProjectCompleteView.as_view(),
        name='project-complete'
    ),
    path(
        '<int:pk>/toggle-participate/',
        views.ToggleParticipateView.as_view(),
        name='toggle-participate'
    ),
]
