from django.conf import settings
from django.db import models

from mailing.models import NULLABLE


class Blog(models.Model):
    header = models.CharField(max_length=100, verbose_name='Заголовок')
    content = models.TextField(**NULLABLE, verbose_name='Содержимое')
    preview = models.ImageField(upload_to='blog/', **NULLABLE, verbose_name='Изображение')
    count_views = models.IntegerField(default=0, verbose_name='Количество просмотров')
    create_date = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Пользователь'
    )

    def __str__(self):
        return f'{self.header} {self.content} {self.count_views}'

    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блоги'