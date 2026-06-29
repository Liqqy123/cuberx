from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from tournaments.models import Tournament
from .forms import RegisterForm, LoginForm
from .models import Booking


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно.')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Авторизация пользователя"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'С возвращением, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form})


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


@login_required
def profile_edit_view(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # Обновление телефона если есть в модели
        if hasattr(user, 'phone'):
            user.phone = request.POST.get('phone', '')
        
        user.save()
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('profile')
    
    return render(request, 'users/profile_edit.html', {'user': request.user})


@login_required
def my_bookings_view(request):
    """Мои бронирования"""
    bookings = Booking.objects.filter(user=request.user).prefetch_related('services')

    total_bookings = bookings.count()
    active_bookings = bookings.filter(status__in=['confirmed', 'pending', 'paid']).count()
    completed_bookings = bookings.filter(status='completed').count()

    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
    }

    return render(request, 'users/my_bookings.html', context)


@login_required
def cancel_booking_view(request, booking_id):
    """Отмена бронирования"""
    if request.method != 'POST':
        return redirect('users:my_bookings')

    booking = Booking.objects.filter(user=request.user, id=booking_id).first()
    if booking:
        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
        messages.warning(request, f'Бронирование #{booking_id} отменено. При необходимости вы можете забронировать другой слот.')
    else:
        messages.error(request, 'Бронирование не найдено.')
    return redirect('users:my_bookings')