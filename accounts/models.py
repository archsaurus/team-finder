import io
import hashlib

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,12}$',
    message='Номер телефона содержит 10–12 цифр и может начинаться с "+".'
)


class UserManager(BaseUserManager):
    def create_user(
        self,
        email, name, surname, password=None,
        **extra_fields
    ):
        if not email:
            raise ValueError('Email - обязателеное поле')

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name, surname=surname,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email, name, surname, password=None,
        **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser должен иметь is_superuser=True.')

        return self.create_user(
            email=email, password=password,
            name=name, surname=surname,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя."""
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/')
    phone = models.CharField(max_length=12, validators=[phone_validator,],)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    favorites = models.ManyToManyField(
        to='projects.Project',
        related_name='favorited_by',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone',]
    objects = UserManager()

    def _first_letter(self) -> str:
        """Безопасно извлекает первую букву имени."""
        return (str(self.name or 'U')[0]).upper()

    def _get_color_index(self, palette):
        """Получает детерминированный индекс цвета из значения поля email."""
        email_hash = hashlib.md5(str(self.email).encode()).hexdigest()

        return int(email_hash, 16) % len(palette)

    def _draw_centered_text(
        self,
        image: Image.Image, text: str,
        font: ImageFont.ImageFont
    ):
        """Отрисовывает центрированный текст на изображении."""
        draw = ImageDraw.Draw(image)

        bbox = draw.textbbox((0, 0), text, font=font)

        text_width = bbox[2] - bbox[0]
        text_height = bbox[3]

        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

        draw.text((x, y), text, fill=(50, 50, 50), font=font)

    def generate_avatar(self):
        """
            Генерирует аватар с первой буквой имени пользователя.
            Создает изображение с цветным фоном и центрированным текстом.
            Сохраняет изображение в поле avatar.
        """
        palette_name = getattr(settings, 'AVATAR_DEFAULT_PALETTE', 'pastel')
        palette = settings.AVATAR_COLOR_PALETTES.get(
            palette_name, settings.AVATAR_COLOR_PALETTES['pastel']
        )

        color_index = self._get_color_index(palette)
        bg_color = palette[color_index]

        img = Image.new('RGB', (100, 100), color=bg_color)

        try:
            font = ImageFont.truetype(
                getattr(
                    settings, 'AVATAR_FONT',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
                ), 48
            )

        except OSError as exc:
            if hasattr(settings, 'logger'):
                settings.logger.warning(
                    f'Не удалось загрузить шрифт: "{exc}". '
                    'Использован шрифт по умолчанию.'
                )

            font = ImageFont.load_default()

        self._draw_centered_text(img, self._first_letter(), font)

        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        self.avatar.save(
            f'{self.email}_avatar.png', ContentFile(output.read()), save=False
        )

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Документация  и формумы утверждают,
        #                            # что такая проверка корректнее проверки
        #                            # по pk.

        if is_new or not self.avatar:
            self.generate_avatar()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.email)
