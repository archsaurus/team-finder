# from django.contrib import admin
# from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),

    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path('users/', include('accounts.urls')),

    path('projects/', include('projects.urls')),

    path(
        '',
        RedirectView.as_view(
            pattern_name='projects:project-list', permanent=False),
        name='root-redirect'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
