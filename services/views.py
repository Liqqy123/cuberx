from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from Users.models import Booking
from .models import ServiceItem


@login_required
def services_view(request):
    """Страница дополнительных услуг."""
    if request.method == 'POST':
        selected_service_ids = request.POST.getlist('services')
        payment_method = request.POST.get('payment_method', '')

        if not selected_service_ids:
            messages.error(request, 'Выберите хотя бы одну услугу для оформления.')
            return redirect('services')

        selected_services = ServiceItem.objects.filter(pk__in=selected_service_ids)
        if not selected_services.exists():
            messages.error(request, 'Выбранные услуги не найдены.')
            return redirect('services')

        total_price = sum(service.price for service in selected_services)
        booking_status = 'pending'
        if payment_method in ('card', 'transfer', 'cash'):
            booking_status = 'paid' if payment_method in ('card', 'transfer') else 'confirmed'

        now = timezone.localtime(timezone.now())
        booking = Booking.objects.create(
            user=request.user,
            pc_name='Услуги',
            booking_date=now.date(),
            booking_time=now.time(),
            duration=1,
            total_price=total_price,
            status=booking_status,
        )
        booking.services.add(*selected_services)

        if payment_method == 'cash':
            messages.success(
                request,
                'Заказ услуг оформлен. Оплата будет произведена наличными на месте.'
            )
        elif payment_method == 'transfer':
            messages.success(
                request,
                'Заказ услуг оформлен. Оплата по QR подтверждена, бронь отмечена как оплаченная.'
            )
        elif payment_method == 'card':
            messages.success(
                request,
                'Заказ услуг оформлен. Оплата картой успешно завершена.'
            )
        else:
            messages.success(request, 'Заказ услуг успешно создан.')

        return redirect('users:my_bookings')

    categories = ['all', 'periphery', 'food', 'premium', 'tournaments']
    service_cards = list(ServiceItem.objects.all().order_by('order', 'name'))

    subscription = {
        'title': 'Кибер-подписка',
        'price': 1990,
        'description': 'Неограниченный доступ к зоне отдыха, скидка на питание и приоритет в турнирах.',
    }

    context = {
        'categories': categories,
        'service_cards': service_cards,
        'subscription': subscription,
    }
    return render(request, 'services/services.html', context)
