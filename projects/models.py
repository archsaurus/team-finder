from django.db import models
from django.urls import reverse

from core import constants


class ProjectStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    CLOSED = 'closed', 'Closed'


class Project(models.Model):
    """Модель проекта."""

    name = models.CharField(verbose_name='Название', max_length=constants.PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(verbose_name='Описание', blank=True)

    owner = models.ForeignKey(
        to='accounts.User',
        verbose_name='Владелец', related_name='owned_projects',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    github_url = models.URLField(verbose_name='GitHub', blank=True)

    status = models.CharField(
        verbose_name='Статус',
        choices=ProjectStatus.choices,
        default=ProjectStatus.OPEN,
        max_length=constants.PROJECT_STATUS_MAX_LENGTH,
        db_index=True,
    )

    participants = models.ManyToManyField(
        to='accounts.User',
        verbose_name='Участники',
        related_name='participated_projects',
        blank=True,
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

        ordering = [
            '-created_at',
        ]

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('projects:project-detail', kwargs={'pk': self.pk})
