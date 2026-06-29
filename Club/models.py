from django.db import models


class ClubInfo(models.Model):
    name = models.CharField('Название клуба', max_length=120, default='CyberX')
    slogan = models.CharField('Слоган', max_length=200, blank=True)
    address = models.CharField('Адрес', max_length=255, blank=True)
    phone = models.CharField('Телефон', max_length=40, blank=True)
    email = models.EmailField('Email', blank=True)
    description = models.TextField('Описание', blank=True)

    profile_games = models.PositiveIntegerField('Всего игр', default=0)
    profile_hours = models.FloatField('Всего часов', default=0.0)
    profile_tournaments = models.PositiveIntegerField('Турниров', default=0)

    class Meta:
        verbose_name = 'Информация о клубе'
        verbose_name_plural = 'Информация о клубе'

    def __str__(self):
        return self.name
