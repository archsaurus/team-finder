import re

from django import forms
from django.core.exceptions import ValidationError

from accounts.models import User


class RegistrationForm(forms.ModelForm):
    """Форма регистрации."""

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email',]

        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'email': 'Эл. почта',
        }

        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError('Пароли не совпадают')

        return cleaned_data


class LoginForm(forms.Form):
    """Форма авторизации."""

    email = forms.EmailField(
        label='Эл. почта',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )


class ChangePasswordForm(forms.Form):
    """Форма смены пароля с кастомной валидацией."""

    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        strip=False,
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        strip=False,
        help_text='Пароль должен содержать минимум 8 символов.'
    )
    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        strip=False,
        help_text='Введите новый пароль ещё раз.'
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if old_password and not self.user.check_password(old_password):
            raise forms.ValidationError('Неверный текущий пароль!')
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Пароли не совпадают!')
        return password2

    def save(self, commit=True):
        """Сохраняет новый пароль."""
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user


class EditProfileForm(forms.ModelForm):
    """Форма редактирования профиля."""

    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'surname': forms.TextInput(attrs={'class': 'form-input'}),
            'about': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'github_url': forms.URLInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url', '').strip()

        if not url:
            return url

        github_pattern = (
            r'^https?://(?:www\.)?github\.com/'
            r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}[A-Za-z0-9])?/?$'
        )

        if not re.match(github_pattern, url):
            raise ValidationError('Ссылка должна вести на GitHub')

        return url
