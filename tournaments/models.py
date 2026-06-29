from django.db import models


class Tournament(models.Model):
    GAME_CHOICES = [
        ('CS2', 'CS2'),
        ('VALORANT', 'VALORANT'),
        ('Dota 2', 'Dota 2'),
        ('Apex Legends', 'Apex Legends'),
        ('PUBG', 'PUBG'),
        ('Fortnite', 'Fortnite'),
    ]
    FORMAT_CHOICES = [
        ('1x1', '1x1'),
        ('5x5', '5x5'),
        ('Solo', 'Solo'),
        ('Duo', 'Duo'),
        ('2x2', '2x2'),
    ]

    title = models.CharField('Название турнира', max_length=150)
    game = models.CharField('Игра', max_length=40, choices=GAME_CHOICES)
    format = models.CharField('Формат', max_length=20, choices=FORMAT_CHOICES)
    date = models.DateTimeField('Дата и время')
    prize = models.PositiveIntegerField('Призовой фонд')
    slots = models.PositiveIntegerField('Заполнено мест')
    max_slots = models.PositiveIntegerField('Всего мест')
    is_online = models.BooleanField('Онлайн', default=True)
    is_featured = models.BooleanField('Главный турнир', default=False)

    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'
        ordering = ('date',)

    def __str__(self):
        return self.title
