from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from services.models import ServiceItem
from tournaments.models import Tournament
from .models import Booking


class HallMapBookingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            phone='+79990001122',
            password='secret123'
        )
        self.service = ServiceItem.objects.create(
            name='Премиум наушники',
            category='periphery',
            price=150,
            description='Наушники'
        )
        self.tournament = Tournament.objects.create(
            title='Cyber Cup',
            game='CS2',
            format='5x5',
            date=timezone.now() + timezone.timedelta(days=1),
            prize=5000,
            slots=12,
            max_slots=32,
            is_featured=True,
        )

    def test_hall_map_post_creates_booking_and_redirects(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('hall_map'),
            {
                'pc_name': 'PC-05',
                'booking_date': '2026-06-20',
                'booking_time': '18:00',
                'duration': '2',
                'services': [str(self.service.id)],
                'total_price': '300',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:my_bookings'))
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.pc_name, 'PC-05')
        self.assertEqual(booking.services.count(), 1)
