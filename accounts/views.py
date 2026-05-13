from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import TextChoices
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView,
    UpdateView,
    FormView,
    ListView,
    RedirectView,
    DetailView,
)
from django.urls import reverse_lazy, reverse

from .forms import LoginForm, RegistrationForm, ChangePasswordForm, EditProfileForm
from .models import User


class UserFilterChoices(TextChoices):
    """Простые фильтры пользователей."""

    FAVORITE_PROJECTS_AUTHORS = (
        'owners-of-favorite-projects',
        'Авторы избранных проектов',
    )
    MY_PROJECTS_PARTICIPANTS = (
        'participants-of-my-projects',
        'Участники моих проектов',
    )
    MY_PROJECTS_FANS = (
        'interested-in-my-projects',
        'Пользователи, которым нравятся мои проекты',
    )
    PARTICIPATED_PROJECTS_AUTHORS = (
        'owners-of-participating-projects',
        'Авторы проектов, где я участвую',
    )


class UserListView(ListView):
    """Список пользователей."""

    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'

    paginate_by = getattr(settings, 'PAGINATION_PAGE_SIZE', 12)

    def _get_filtered_users(self, user, filter_type):
        filters = {
            UserFilterChoices.FAVORITE_PROJECTS_AUTHORS: {
                'owned_projects__in': user.favorites.all()
            },
            UserFilterChoices.MY_PROJECTS_PARTICIPANTS: {
                'participated_projects__owner': user
            },
            UserFilterChoices.MY_PROJECTS_FANS: {'favorites__owner': user},
            UserFilterChoices.PARTICIPATED_PROJECTS_AUTHORS: {
                'owned_projects__participants': user
            },
        }

        filter_params = filters.get(filter_type)

        if not filter_params:
            return User.objects.none()

        return (
            User.objects.filter(**filter_params)
            .prefetch_related('participated_projects', 'owned_projects')
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            active_filter = self.request.GET.get('filter')
            context.update(
                {
                    'active_filter': active_filter,
                    'active_skill': next(
                        (
                            choice[1]
                            for choice in UserFilterChoices.choices
                            if choice[0] == active_filter
                        ),
                        None,
                    ),
                    'filter_choices': UserFilterChoices.choices,
                }
            )

        return context

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.all()

        filter_type = self.request.GET.get('filter')

        if filter_type not in UserFilterChoices.values:
            return User.objects.all()

        return self._get_filtered_users(self.request.user, filter_type)


class UserDetailView(DetailView):
    """Страница пользователя."""

    model = User
    template_name = 'users/user-details.html'


class RegisterView(CreateView):
    """Форма регистрации."""

    template_name = 'users/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('projects:project-list')

    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)
            self.object.set_password(form.cleaned_data['password'])
            self.object.save()

            login(self.request, self.object)

            return HttpResponseRedirect(self.get_success_url())

        except IntegrityError:
            form.add_error('email', 'Пользователь с таким email уже существует')
            return self.form_invalid(form)


class LoginView(FormView):
    """Форма авторизации."""

    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('projects:project-list')

    def form_valid(self, form):
        user = authenticate(
            self.request,
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )

        if user is None:
            form.add_error(None, 'Неверный email или пароль')
            return self.form_invalid(form)

        login(self.request, user)

        return HttpResponseRedirect(self.get_success_url())


class LogoutView(LoginRequiredMixin, RedirectView):
    """Выход из аккаунта."""

    url = reverse_lazy('projects:project-list')

    def get(self, request, *args, **kwargs):
        logout(request)

        return super().get(request, *args, **kwargs)


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    form_class = ChangePasswordForm
    template_name = 'users/change_password.html'

    def get_success_url(self):
        """Динамический URL на профиль пользователя."""
        return reverse('users:user-details', kwargs={'pk': self.request.user.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()

        if user.is_authenticated:
            update_session_auth_hash(self.request, user)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = EditProfileForm
    template_name = 'users/edit_profile.html'

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('users:user-details', kwargs={'pk': self.request.user.pk})
