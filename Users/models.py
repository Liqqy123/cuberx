from django.contrib.auth.models import AbstractUser
from django.db import models

from services.models import ServiceItem


class CustomUser(AbstractUser):
    phone = models.CharField(
        max_length=15,
        unique=True,
        verbose_name='Телефон',
        help_text='Номер телефона с кодом страны (например, +79991234567)'
    )
    email = models.EmailField(unique=True, verbose_name='Email')

    profile_games = models.PositiveIntegerField('Всего игр', default=0)
    profile_hours = models.FloatField('Всего часов', default=0.0)
    profile_tournaments = models.PositiveIntegerField('Турниров', default=0)

    def __str__(self):
        return self.username


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Подтверждено'),
        ('paid', 'Оплачено'),
        ('pending', 'Ожидает'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Пользователь'
    )
    pc_name = models.CharField('Компьютер', max_length=50)
    booking_date = models.DateField('Дата бронирования')
    booking_time = models.TimeField('Время бронирования')
    duration = models.PositiveIntegerField('Длительность (часы)', default=1)
    status = models.CharField('Статус', max_length=12, choices=STATUS_CHOICES, default='pending')
    total_price = models.PositiveIntegerField('Сумма', default=0)
    services = models.ManyToManyField(
        ServiceItem,
        blank=True,
        related_name='bookings',
        verbose_name='Услуги'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ('-booking_date', '-booking_time')

    def __str__(self):
        return f'Бронирование #{self.pk} ({self.user.username})'