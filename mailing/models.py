from django.conf import settings
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    email = models.EmailField(max_length=254, verbose_name='почта')
    comment = models.TextField(**NULLABLE, verbose_name='комментарий')
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Пользователь'
    )

    def __str__(self):
        return f'{self.email} ({self.full_name})'

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'


class Message(models.Model):
    message_subject = models.CharField(default='Тема', max_length=255, verbose_name='тема')
    message_body = models.TextField(default='Описание', verbose_name='письмо')

    def __str__(self):
        return f'{self.message_subject} {self.message_body}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailing(models.Model):
    D = "D"
    W = "W"
    M = "M"

    MAILING_PERIODS = (
        (D, 'Каждый день'),
        (W, 'Каждую неделю'),
        (M, 'Каждый месяц'),
    )

    CREATED = 'Created'
    STARTED = 'Started'
    STOPPED = 'Stopped'

    STATUS = (
        (CREATED, 'Создана'),
        (STARTED, 'Запущена'),
        (STOPPED, 'Завершена'),
    )
    time_start = models.TimeField(default='9:00', verbose_name='время старта рассылки')
    time_stop = models.TimeField(default='00:00', verbose_name='время окончания рассылки')
    mailing_period = models.CharField(**NULLABLE, choices=MAILING_PERIODS, default=D, verbose_name='период рассылки')
    status = models.CharField(max_length=50, default=CREATED, choices=STATUS, verbose_name='Статус')
    message = models.ForeignKey(Message, **NULLABLE, on_delete=models.CASCADE, verbose_name='сообщение')
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Пользователь'
    )

    def __str__(self):
        return f"Рассылка:({self.id})"

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class ClientMailing(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка клиента')

    def __str__(self):
        return f'{self.client} / {self.mailing}'

    class Meta:
        verbose_name = 'Рассылка клиента'
        verbose_name_plural = 'Рассылка клиентов'


class Log(models.Model):
    STATUS_OK = 'success'
    STATUS_FAILED = 'failure'

    MAILING_STATUS = (
        (STATUS_OK, 'Выполнено'),
        (STATUS_FAILED, 'Ошибка'),
    )

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='сообщение')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='дата попытки')
    status = models.CharField(max_length=50, choices=MAILING_STATUS, default=STATUS_OK, verbose_name='статус')
    response = models.TextField(**NULLABLE, verbose_name='Ответ от сервиса')

    def __str__(self):
        return str(self.date_time)

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
