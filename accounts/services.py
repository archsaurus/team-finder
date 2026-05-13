import io
import hashlib
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from .models import User


def _first_letter(user: User) -> str:
    """Безопасно извлекает первую букву имени."""
    return (str(user.name or 'U')[0]).upper()


def _get_color_index(user: User, palette):
    """Получает детерминированный индекс цвета из значения поля email."""
    email_hash = hashlib.md5(str(user.email).encode()).hexdigest()

    return int(email_hash, 16) % len(palette)


def _draw_centered_text(image: Image.Image, text: str, font: ImageFont.ImageFont):
    """Отрисовывает центрированный текст на изображении."""
    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0, 0), text, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3]

    x = (image.width - text_width) / 2
    y = (image.height - text_height) / 2

    draw.text((x, y), text, fill=(50, 50, 50), font=font)


def generate_avatar(user: User):
    """
    Генерирует аватар с первой буквой имени пользователя.
    Создает изображение с цветным фоном и центрированным текстом.
    Сохраняет изображение в поле avatar.
    """
    palette_name = getattr(settings, 'AVATAR_DEFAULT_PALETTE', 'pastel')
    palette = settings.AVATAR_COLOR_PALETTES.get(
        palette_name, settings.AVATAR_COLOR_PALETTES['pastel']
    )

    color_index = _get_color_index(user, palette)
    bg_color = palette[color_index]

    img = Image.new('RGB', getattr(settings, 'AVATAR_SIZE', (100, 100)), color=bg_color)

    try:
        font = ImageFont.truetype(
            getattr(
                settings,
                'AVATAR_FONT',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            ),
            48,
        )

    except OSError as exc:
        if hasattr(settings, 'logger'):
            settings.logger.warning(
                f'Не удалось загрузить шрифт: "{exc}". Использован шрифт по умолчанию.'
            )

        font = ImageFont.load_default()

    _draw_centered_text(img, _first_letter(user), font)

    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)

    user.avatar.save(f'{user.email}_avatar.png', ContentFile(output.read()))
