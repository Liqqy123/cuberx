from faker import Faker

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from Club.models import ClubInfo
from services.models import ServiceItem
from tournaments.models import Tournament
from Users.models import Booking


def home_view(request):
    """Главная страница клуба."""
    club = ClubInfo.objects.first()
    featured_services = list(ServiceItem.objects.filter(is_featured=True).order_by('order', 'name')[:4])
    if len(featured_services) < 4:
        featured_services = list(ServiceItem.objects.order_by('order', 'name')[:4])

    featured_tournaments = list(Tournament.objects.filter(is_featured=True).order_by('date')[:4])
    if len(featured_tournaments) < 4:
        featured_tournaments = list(Tournament.objects.order_by('date')[:4])

    next_tournament = Tournament.objects.filter(date__gte=timezone.now()).order_by('date').first()

    fake = Faker('ru_RU')
    reviews = []
    for _ in range(6):
        author = fake.name()
        game = fake.random_element(elements=['CS2', 'Valorant', 'Dota 2', 'PUBG', 'Fortnite', 'Apex Legends'])
        quote = fake.sentence(nb_words=10).rstrip('.')
        reviews.append({
            'author': author,
            'avatar': author[0].upper(),
            'game': game,
            'quote': f'«{quote}»',
            'time': fake.random_element(elements=['2 дня назад', 'неделю назад', '3 дня назад', '5 дней назад', '1 день назад', 'сегодня']),
        })

    context = {
        'title': f"{club.name if club else 'CyberX'} - Киберспортивный клуб",
        'club': club,
        'featured_services': featured_services,
        'featured_tournaments': featured_tournaments,
        'next_tournament': next_tournament,
        'hero_title': 'CYBER',
        'hero_subtitle': club.slogan if club and club.slogan else 'Мощное железо, топовая периферия и свой уютный клуб',
        'reviews': reviews,
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    """Страница о клубе"""
    return render(request, 'pages/about.html')


def contacts_view(request):
    """Страница контактов"""
    club = ClubInfo.objects.first()
    context = {
        'club': club,
    }
    return render(request, 'pages/contacts.html', context)


@login_required
def profile_view(request):
    """Личный кабинет пользователя"""
    tournaments = Tournament.objects.all().order_by('date')
    upcoming_tournaments = tournaments.filter(date__gte=timezone.now())[:3]
    past_tournaments = tournaments.filter(date__lt=timezone.now()).order_by('-date')[:3]

    context = {
        'user': request.user,
        'upcoming_tournaments': upcoming_tournaments,
        'past_tournaments': past_tournaments,
        'all_tournaments_count': tournaments.count(),
    }
    return render(request, 'users/profile.html', context)


def hall_map_view(request):
    """Карта зала с компьютерами."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Для бронирования нужно войти в аккаунт.')
            return redirect('users:login')

        pc_name = request.POST.get('pc_name', '').strip()
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')
        duration = request.POST.get('duration', '1')
        total_price = request.POST.get('total_price', '0')
        payment_method = request.POST.get('payment_method', '')

        if not all([pc_name, booking_date, booking_time]):
            messages.error(request, 'Пожалуйста, выберите компьютер, дату и время.')
            return redirect('hall_map')

        try:
            booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            messages.error(request, 'Неверный формат даты бронирования.')
            return redirect('hall_map')

        if booking_date < timezone.localdate():
            messages.error(request, 'Нельзя бронировать компьютер на прошедшую дату.')
            return redirect('hall_map')

        try:
            duration = int(duration)
        except (TypeError, ValueError):
            duration = 1

        try:
            start_hour, start_minute = map(int, booking_time.split(':'))
            booking_start = start_hour * 60 + start_minute
        except (TypeError, ValueError):
            messages.error(request, 'Неверный формат времени бронирования.')
            return redirect('hall_map')

        booking_end = booking_start + duration * 60

        existing_conflicts = Booking.objects.filter(pc_name=pc_name, booking_date=booking_date)
        for existing in existing_conflicts:
            existing_start = existing.booking_time.hour * 60 + existing.booking_time.minute
            existing_end = existing_start + existing.duration * 60
            if existing_start < booking_end and booking_start < existing_end:
                messages.error(request, 'Выбранный компьютер уже занят в указанное время.')
                return redirect('hall_map')

        try:
            total_price = int(total_price)
        except (TypeError, ValueError):
            total_price = 0

        selected_services = ServiceItem.objects.filter(pk__in=request.POST.getlist('services'))
        service_total = sum(service.price for service in selected_services)

        if duration > 0:
            base_total = max(total_price, 0)
            fallback_total = service_total * duration
            if base_total == 0:
                total_price = fallback_total
            elif base_total < fallback_total:
                total_price = base_total

        booking_status = 'pending'
        if payment_method in ('card', 'transfer', 'cash'):
            booking_status = 'paid' if payment_method in ('card', 'transfer') else 'confirmed'

        booking = Booking.objects.create(
            user=request.user,
            pc_name=pc_name,
            booking_date=booking_date,
            booking_time=booking_time,
            duration=duration,
            total_price=total_price or 0,
            status=booking_status,
        )
        booking.services.add(*selected_services)

        if payment_method == 'cash':
            messages.success(
                request,
                f'Бронирование для {pc_name} подтверждено. Оплата будет произведена наличными на месте.'
            )
        elif payment_method == 'transfer':
            messages.success(
                request,
                f'Бронирование для {pc_name} подтверждено. Оплата по QR оформлена, бронь отмечена как оплаченная.'
            )
        elif payment_method == 'card':
            messages.success(
                request,
                f'Бронирование для {pc_name} подтверждено. Оплата картой успешно оформлена.'
            )
        else:
            messages.success(request, f'Бронирование для {pc_name} успешно создано!')

        return redirect('users:my_bookings')

    club = ClubInfo.objects.first()

    pc_cards = [
        {
            'id': f'PC-{i}',
            'type': 'standard',
            'price': 140,
            'status': 'available',
            'status_class': 'status-available',
            'status_text': 'Свободно',
            'gpu': 'RTX 3060',
            'ram': '16GB RAM',
            'refresh': '144Hz',
        }
        for i in range(1, 11)
    ]
    vip_cards = [
        {
            'id': f'VIP-{i}',
            'type': 'vip',
            'price': 200,
            'status': 'available',
            'status_class': 'status-available',
            'status_text': 'Свободно',
            'gpu': 'RTX 4090',
            'ram': '64GB RAM',
            'refresh': '360Hz',
            'extra': 'Премiум кресло'
        }
        for i in range(1, 9)
    ]

    booking_services = list(ServiceItem.objects.exclude(category='tournaments')[:4])
    if len(booking_services) < 4:
        booking_services = [
            {'icon': 'fa-headphones', 'name': 'Премиум наушники', 'price': 100, 'category': 'periphery'},
            {'icon': 'fa-mouse', 'name': 'Игровая мышь', 'price': 80, 'category': 'periphery'},
            {'icon': 'fa-keyboard', 'name': 'Механическая клавиатура', 'price': 120, 'category': 'periphery'},
            {'icon': 'fa-coffee', 'name': 'Энергетический напиток', 'price': 50, 'category': 'food'},
        ]

    context = {
        'club': club,
        'pc_cards': pc_cards,
        'vip_cards': vip_cards,
        'booking_services': booking_services,
        'today': timezone.localdate(),
    }
    return render(request, 'pages/hall_map.html', context)


# ============ ОБРАБОТЧИКИ ОШИБОК ============

def custom_bad_request(request, exception=None):
    """Кастомная страница 400 - Некорректный запрос"""
    return render(request, 'errors/400.html', status=400)


def custom_permission_denied(request, exception=None):
    """Кастомная страница 403 - Доступ запрещен"""
    return render(request, 'errors/403.html', status=403)


def custom_page_not_found(request, exception=None):
    """Кастомная страница 404 - Страница не найдена"""
    return render(request, 'errors/404.html', status=404)


def custom_server_error(request):
    """Кастомная страница 500 - Внутренняя ошибка сервера"""
    return render(request, 'errors/500.html', status=500)


