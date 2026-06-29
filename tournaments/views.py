from django.shortcuts import render
from django.utils import timezone

from .models import Tournament


def tournaments_view(request):
    """Страница турниров."""
    tournaments = list(Tournament.objects.all().order_by('date'))
    upcoming = [t for t in tournaments if t.date >= timezone.now()][:3]

    featured_tournament = next((t for t in tournaments if t.is_featured), tournaments[0] if tournaments else None)

    context = {
        'banner_game': featured_tournament.title if featured_tournament else 'Турниры CyberX',
        'banner_prize': featured_tournament.prize if featured_tournament else 0,
        'featured_tournament': featured_tournament,
        'upcoming': upcoming,
        'tournaments': tournaments,
    }
    return render(request, 'tournaments/tournaments.html', context)
