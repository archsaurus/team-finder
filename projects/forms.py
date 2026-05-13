from django import forms
from django.core.validators import URLValidator

from .models import Project


class GitHubURLValidator(URLValidator):
    """Валидатор только для GitHub ссылок."""

    def __call__(self, value):
        if not value.startswith(('https://github.com/', 'http://github.com/')):
            raise forms.ValidationError('Ссылка должна вести на GitHub')
        super().__call__(value)


class ProjectForm(forms.ModelForm):
    """Форма создания/редактирования проекта."""

    github_url = forms.URLField(
        label='Ссылка на GitHub',
        required=False,
        validators=[GitHubURLValidator()],
        widget=forms.URLInput(
            attrs={'placeholder': 'https://github.com/username/repo'}
        ),
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        labels = {
            'name': 'Название проекта',
            'description': 'Описание',
            'status': 'Статус',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Введите название проекта'}),
            'description': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Расскажите о вашем проекте...'}
            ),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
