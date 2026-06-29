from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from Club.models import ClubInfo
from services.models import ServiceItem
from tournaments.models import Tournament
from Users.models import Booking, CustomUser


class Command(BaseCommand):
    help = 'Заполняет сайт красивыми примерными данными для всех разделов'

    def handle(self, *args, **options):
        fake = Faker('ru_RU')

        club, _ = ClubInfo.objects.update_or_create(
            pk=1,
            defaults={
                'name': 'CyberX',
                'slogan': 'Киберспортивный клуб нового поколения',
                'address': 'г. Белореченск, ул. Мира, 164',
                'phone': '+7 (918) 216-41-64',
                'email': 'info@cyberx.ru',
                'description': (
                    'CyberX — это место, где встречаются геймеры, стримеры и команды. '
                    'У нас комфортные зоны, мощные ПК, уютный бар и регулярные турниры.'
                ),
            }
        )

        ServiceItem.objects.all().delete()
        services = [
            {
                'name': 'Премиум наушники',
                'category': 'periphery',
                'description': 'Премиальные гарнитуры с высоким уровнем комфорта и чистым звуком.',
                'price': 120,
                'period': '/час',
                'icon': 'fa-headphones',
                'is_featured': True,
                'order': 1,
            },
            {
                'name': 'Игровая мышь',
                'category': 'periphery',
                'description': 'Точная мышь для соревновательных матчей и комфортной игры.',
                'price': 90,
                'period': '/час',
                'icon': 'fa-mouse',
                'is_featured': True,
                'order': 2,
            },
            {
                'name': 'Механическая клавиатура',
                'category': 'periphery',
                'description': 'Клавиатуры с быстрым откликом и яркой RGB-подсветкой.',
                'price': 140,
                'period': '/час',
                'icon': 'fa-keyboard',
                'is_featured': False,
                'order': 3,
            },
            {
                'name': 'Бургер с говядиной',
                'category': 'food',
                'description': 'Сочный бургер, картофель фри и фирменный соус.',
                'price': 320,
                'period': '',
                'icon': 'fa-hamburger',
                'is_featured': False,
                'order': 4,
            },
            {
                'name': 'Латте с сиропом',
                'category': 'food',
                'description': 'Тёплый кофейный напиток для перерыва между матчами.',
                'price': 210,
                'period': '',
                'icon': 'fa-coffee',
                'is_featured': False,
                'order': 5,
            },
            {
                'name': 'VIP-комната',
                'category': 'premium',
                'description': 'Приватная зона для стримов, тренировок и отдыха команды.',
                'price': 3500,
                'period': '/5 часов',
                'icon': 'fa-crown',
                'is_featured': True,
                'order': 6,
            },
            {
                'name': 'Турнирный пакет',
                'category': 'tournaments',
                'description': 'Пакет для участия в турнире с приоритетной регистрацией.',
                'price': 600,
                'period': '',
                'icon': 'fa-trophy',
                'is_featured': True,
                'order': 7,
            },
        ]

        for service in services:
            ServiceItem.objects.create(**service)

        Tournament.objects.all().delete()
        base_date = timezone.now().replace(hour=18, minute=0, second=0, microsecond=0)
        game_choices = [choice[0] for choice in Tournament.GAME_CHOICES]
        format_choices = [choice[0] for choice in Tournament.FORMAT_CHOICES]

        tournament_payloads = []
        for i in range(6):
            game = fake.random_element(elements=game_choices)
            format_value = fake.random_element(elements=format_choices)
            tournament_date = base_date + timedelta(
                days=i * 3 + fake.random_int(min=0, max=2),
                hours=fake.random_int(min=16, max=22),
                minutes=fake.random_element(elements=[0, 15, 30, 45]),
            )
            slots = fake.random_int(min=4, max=18)
            max_slots = slots + fake.random_int(min=4, max=12)
            tournament_payloads.append(
                {
                    'title': fake.random_element(
                        elements=[
                            f'{game} {format_value} Cup',
                            f'{game} {format_value} League',
                            f'{game} {format_value} Showdown',
                            f'{game} {format_value} Arena',
                        ]
                    ),
                    'game': game,
                    'format': format_value,
                    'date': tournament_date,
                    'prize': fake.random_int(min=15000, max=150000),
                    'slots': slots,
                    'max_slots': max_slots,
                    'is_online': fake.boolean(chance_of_getting_true=60),
                    'is_featured': i == 0 or fake.boolean(chance_of_getting_true=20),
                }
            )

        for payload in tournament_payloads:
            Tournament.objects.create(**payload)

        # Faker-данные для пользовательских броней
        users = list(CustomUser.objects.all())
        if not users:
            self.stdout.write(self.style.WARNING('Нет пользователей для генерации броней.'))
        else:
            Booking.objects.all().delete()
            statuses = ['confirmed', 'pending', 'completed', 'cancelled']
            for user in users:
                for _ in range(fake.random_int(min=1, max=3)):
                    booking_date = fake.date_between(start_date='-30d', end_date='+30d')
                    booking_time = fake.time_object()
                    duration = fake.random_int(min=1, max=5)
                    services = ServiceItem.objects.order_by('?')[:fake.random_int(min=0, max=3)]
                    total_price = fake.random_int(min=300, max=1800)
                    if services:
                        total_price = sum(service.price for service in services) * duration
                    booking = Booking.objects.create(
                        user=user,
                        pc_name=fake.random_element(elements=['PC-01', 'PC-07', 'PC-12', 'VIP-3', 'VIP-5']),
                        booking_date=booking_date,
                        booking_time=booking_time,
                        duration=duration,
                        status=fake.random_element(elements=statuses),
                        total_price=total_price,
                    )
                    booking.services.add(*services)

        self.stdout.write(self.style.SUCCESS('Seed-данные успешно загружены.'))