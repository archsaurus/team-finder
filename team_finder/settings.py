from pathlib import Path
import ast
import logging

from decouple import config


logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS_STR = config('DJANGO_ALLOWED_HOSTS', default='["*"]')
ALLOWED_HOSTS = ast.literal_eval(ALLOWED_HOSTS_STR)

# region Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR) / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
# endregion


# region Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# endregion


AUTH_USER_MODEL = 'accounts.User'

# region Accounts Application Settings
AVATAR_COLOR_PALETTES = {
    'pastel': [
        (200, 220, 255), (255, 220, 200),
        (220, 255, 220), (255, 200, 220),
        (240, 230, 255), (255, 240, 200),
        (200, 255, 240), (255, 200, 255)
    ],
    'soft': [
        (180, 200, 230), (230, 190, 170),
        (170, 220, 190), (230, 170, 200)
    ],
    'professional': [
        (160, 190, 220), (200, 180, 160),
        (160, 200, 180), (220, 160, 190)
    ]
}

AVATAR_DEFAULT_PALETTE = 'pastel'

AVATAR_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
# endregion

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',

    'accounts',
    'projects',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'team_finder.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / f'templates_var{config('TASK_VERSION', default='1')}',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'team_finder.wsgi.application'


# region Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST', default='db'),
        'PORT': config('POSTGRES_PORT', default=5432, cast=int),
    }
}
# endregion


# region Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []
if not DEBUG:
    AUTH_PASSWORD_VALIDATORS.extend(
        [
            {
                'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
            },
            {
                'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
            },
            {
                'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
            },
            {
                'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
            },
        ]
    )
# endregion


# region Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
# endregion


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# region REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}
# endregion
