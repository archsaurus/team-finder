from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, View
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .forms import ProjectForm
from .models import Project, ProjectStatus, UserProject


class ProjectListView(ListView):
    """Список проектов, отсортированных от новых к старым.
        Шаблон: templates/projects/project_list.html
    """
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        return Project.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['favorites'] = set(
                self.request.user.favorites.values_list('pk', flat=True)
            )

        return context


class ProjectDetailView(DetailView):
    """Страница проекта."""
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        """Добавляет контекст: владелец, участники, избранное."""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        project = self.object

        context.update({
            'owner': project.owner,
            'participants': project.participants.all(),
            'is_favorited': (
                self.request.user.is_authenticated
                and self.request.user.favorites.filter(pk=project.pk).exists()
            ),
            'participants_count': project.participants.count(),
        })
        return context

    def get_queryset(self):
        return (
            Project.objects
            .select_related('owner')
            .prefetch_related('participants')
        )


class ToggleFavoriteAPIView(APIView):
    """POST /<project_id>/toggle-favorite/
        Требует аутентификации (JWT, Session и т.п.).
        Возвращает JSON:
            {"status": "ok", "favorited": true/false}
    """
    permission_classes = [IsAuthenticated, ]

    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        user = request.user

        is_favorited = user.favorites.filter(pk=project.pk).exists()

        if is_favorited:
            user.favorites.remove(project)
            favorited = False

        else:
            user.favorites.add(project)
            favorited = True

        return Response(
            {"status": "ok", "favorited": favorited},
            status=status.HTTP_200_OK
        )


class FavoriteProjectListView(LoginRequiredMixin, ListView):
    """Страница избранного."""
    model = Project
    template_name = 'projects/favorite_projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return (
            self.request.user.favorites
            .all()
            .order_by('-created_at')
        )


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Создание проекта."""
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()

        project.participants.add(self.request.user)
        return HttpResponseRedirect(project.get_absolute_url())

    def get_success_url(self):
        return reverse(
            'projects:project-detail', kwargs={'pk': self.object.pk}
        )


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование проекта."""
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse(
            'projects:project-detail', kwargs={'pk': self.object.pk}
        )



class ProjectCompleteView(LoginRequiredMixin, View):
    """Завершение проекта (AJAX)."""

    def post(self, request, pk):
        project = get_object_or_404(
            Project, pk=pk, owner=request.user
        )

        if project.status == ProjectStatus.CLOSED:
            return JsonResponse({
                'status': 'error',
                'message': 'Проект уже завершен'
            })

        project.status = ProjectStatus.CLOSED
        project.save()

        return JsonResponse({
            'status': 'ok',
            'message': 'Проект завершен'
        })


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        user = request.user

        # Логируем для дебага
        print(f"User {user.id}, Project {pk}")

        if UserProject.objects.filter(user=user, project=project).exists():
            UserProject.objects.filter(user=user, project=project).delete()
            is_participant = False
        else:
            UserProject.objects.create(user=user, project=project)
            is_participant = True

        count = UserProject.objects.filter(project=project).count()

        return JsonResponse({
            'status': 'ok',
            'participant': is_participant,
            'participants_count': count,
            'debug': {
                'user_id': user.id,
                'project_id': project.id
            }
        })
