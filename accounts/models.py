from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,12}$',
    message='Номер телефона содержит 10–12 цифр и может начинаться с '+'.',
)


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email - обязателеное поле')

        email = self.normalize_email(email)

        user = self.model(email=email, name=name, surname=surname, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser должен иметь is_superuser=True.')

        return self.create_user(
            email=email, password=password, name=name, surname=surname, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя."""

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        ordering = [
            'pk',
        ]

    email = models.EmailField(verbose_name='Email', unique=True, db_index=True)
    name = models.CharField(
        verbose_name='Имя', max_length=getattr(settings, 'NAMING_FIELD_MAX_LENGTH', 124)
    )
    surname = models.CharField(
        verbose_name='Фамилия',
        max_length=getattr(settings, 'NAMING_FIELD_MAX_LENGTH', 124),
    )
    avatar = models.ImageField(verbose_name='Аватар', upload_to='avatars/')
    phone = models.CharField(
        verbose_name='Телефон',
        max_length=getattr(settings, 'PHONE_MAX_LENGTH', 12),
        validators=[
            phone_validator,
        ],
    )
    github_url = models.URLField(verbose_name='GitHub', blank=True)
    about = models.TextField(
        verbose_name='О себе',
        max_length=getattr(settings, 'USER_BIO_MAX_LENGTH', 256),
        blank=True,
    )
    is_active = models.BooleanField(verbose_name='Активен', default=True)
    is_staff = models.BooleanField(verbose_name='Статус персонала', default=False)

    favorites = models.ManyToManyField(
        to='projects.Project', related_name='favorited_by', blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'name',
        'surname',
        'phone',
    ]
    objects = UserManager()

    def __str__(self):
        return self.email
