'''Скрипт для генерации тестовых данных сервиса teamfinder.'''

import random

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from faker import Faker

from accounts.models import User
from accounts.services import generate_avatar
from projects.models import Project, ProjectStatus

UserModel = get_user_model()
fake = Faker('ru_RU')

USERS = 64
PROJECTS = 256
SEED = 42

PASSWORD = 'testpass123'
SUPERUSER_PASSWORD = 'testpass_superuser'
SUPERUSER_EMAIL = 'chupa@kabra.usi'


class Command(BaseCommand):
    help = f'Создает тестовые данные: {USERS} пользователя, {PROJECTS} проекта'

    def add_arguments(self, parser):
        parser.add_argument(
            '--seed', type=int, default=SEED, help='Seed для воспроизводимости'
        )

    def handle(self, *args, **options):
        random.seed(options['seed'])
        Faker.seed(options['seed'])

        self.stdout.write('Очистка старых тестовых данных...')

        User.objects.filter(email__startswith='testuser').delete()
        Project.objects.filter(name__startswith='Проект').delete()

        self.stdout.write('Создание суперпользователя...')
        superuser, created = User.objects.get_or_create(
            email=SUPERUSER_EMAIL,
            defaults={
                'name': 'Чупакабра',
                'surname': 'Пангасиус', 
                'phone': '+66666666666',
                'is_superuser': True,
                'is_staff': True,
            }
        )
        if created:
            superuser.set_password(SUPERUSER_PASSWORD)
            superuser.save()
            generate_avatar(superuser)
            self.stdout.write(self.style.SUCCESS('Чупакабра создана!'))

        self.stdout.write('Создание пользователей...')
        users = []
        for i in range(0, USERS):
            user = User.objects.create_user(
                email=f'testuser{i}@example.com',
                name=fake.first_name(),
                surname=fake.last_name(),
                phone=f'+79{random.randint(100000000, 999999999):09d}',
                password=PASSWORD,
                github_url=f'https://github.com/{slugify(fake.user_name())}',
                about=fake.sentence(nb_words=10),
            )

            generate_avatar(user)

            users.append(user)

        self.stdout.write(self.style.SUCCESS(f'Создано {len(users)} пользователей'))

        self.stdout.write('Создание проектов...')
        projects = []
        statuses = [ProjectStatus.OPEN, ProjectStatus.CLOSED]

        for i in range(PROJECTS):
            project = Project.objects.create(
                name=f'Проект {i}',
                description=(
                    f'Описание проекта {i}. '
                    f'{fake.sentence(nb_words=random.randint(15, 128))}'
                ),
                # Владельцы циклически из первых 8 юзеров
                owner=users[(i - 1) % 8],
                github_url=f'https://github.com/testorg/project-{i}',
                status=random.choice(statuses),
            )

            projects.append(project)

        self.stdout.write(self.style.SUCCESS(f'Создано {len(projects)} проектов'))

        self.stdout.write('Распределение участников по проектам...')
        project_participant_counts = []

        for project in projects:
            num_participants = random.randint(0, 8)
            project_participant_counts.append(num_participants)

            if num_participants > 0:
                available_users = [u for u in users if u != project.owner]
                selected_users = random.sample(available_users, num_participants)

                project.participants.add(*selected_users)

        self.stdout.write(self.style.SUCCESS(f'Участники распределены'))

        # (30% пользователей лайкают 1-3 случайных проекта)
        self.stdout.write('Создание избранных проектов...')
        favorite_counts = 0

        for user in users:
            if random.random() < 0.3:
                num_favorites = random.randint(1, 3)
                favorite_projects = random.sample(projects, num_favorites)
                user.favorites.add(*favorite_projects)
                favorite_counts += num_favorites

        self.stdout.write(self.style.SUCCESS(f'Добавлено {favorite_counts} избранных'))

        self.stdout.write(self.style.SUCCESS(f'\nСТАТИСТИКА:'))
        self.stdout.write(f'\tПользователей: {len(users)}')
        self.stdout.write(f'\tПроектов: {len(projects)}')
        self.stdout.write(
            f'\tОткрытых проектов: {
                Project.objects.filter(status=ProjectStatus.OPEN).count()
            }'
        )

        min_participants = min(project_participant_counts)
        max_participants = max(project_participant_counts)
        avg_participants = sum(project_participant_counts) / len(
            project_participant_counts
        )

        self.stdout.write(
            '\tУчастников по проектам: '
            f'{min_participants}-{max_participants} '
            f'(ср. {avg_participants:.1f})'
        )

        self.stdout.write(f'\tИзбранных связей: {favorite_counts}')

        self.stdout.write(self.style.WARNING(f'\nЛогин/Пароль:'))
        self.stdout.write(f'\tСупер-пользователь: {SUPERUSER_EMAIL} / {SUPERUSER_PASSWORD}')
        self.stdout.write(f'\tПолзователь: testuser1@example.com / {PASSWORD}')

        self.stdout.write(
            self.style.SUCCESS(f'\nТестовые данные успешно созданы. Зерно: {SEED}')
        )
