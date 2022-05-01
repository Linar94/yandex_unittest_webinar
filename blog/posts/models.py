from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.db import models

# Create your models here.


User = get_user_model()


class Group(models.Model):
    """ Модель для создания группы в соц.сети. """

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    """ Модель для создания поста в соц.сети. """

    text = models.TextField(
        help_text="Введите текст поста",
        validators=[MaxLengthValidator(50, "Превышено максимальное количество символов")]
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Выберите группу поста"
    )

    class Meta:
        ordering = ('-pub_date',)