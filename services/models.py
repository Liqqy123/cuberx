from autoslug import AutoSlugField
from django.db import models


class ServiceItem(models.Model):
    CATEGORY_CHOICES = [
        ('periphery', 'Периферия'),
        ('food', 'Кухня и бар'),
        ('premium', 'Премиум'),
        ('tournaments', 'Турниры'),
    ]

    name = models.CharField('Название услуги', max_length=120)
    slug = AutoSlugField(populate_from='name', unique=True, always_update=True)
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField('Описание', blank=True)
    price = models.PositiveIntegerField('Цена')
    image = models.ImageField('Изображение', upload_to='services/', blank=True, null=True) 
    period = models.CharField('Период', max_length=50, blank=True)
    icon = models.CharField('Иконка', max_length=50, default='fa-star')
    is_featured = models.BooleanField('Показывать как рекомендуемую', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name
