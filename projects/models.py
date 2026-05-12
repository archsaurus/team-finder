from django.db import models
from django.urls import reverse


class ProjectStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    CLOSED = 'closed', 'Closed'


class Project(models.Model):
    """Модель проекта."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    owner = models.ForeignKey(
        to='accounts.User',
        related_name='owned_projects',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)

    status = models.CharField(
        choices=ProjectStatus.choices,
        default=ProjectStatus.OPEN,
        max_length=6,
        db_index=True
    )

    participants = models.ManyToManyField(
        to='accounts.User',
        through='projects.UserProject',
        related_name='participated_projects',
        blank=True
    )

    def get_absolute_url(self):
        return reverse('projects:project-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.name)


class UserProject(models.Model):
    """Модель связи между пользователем и проектом."""
    user = models.ForeignKey(
        to='accounts.User', on_delete=models.CASCADE
    )

    project = models.ForeignKey(
        to='projects.Project', on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'project'],
                name='unique_user_project')
        ]

    def __str__(self):
        return f'{self.user.email} - {self.project.name}'
