from django.contrib import admin
from .models import ClubInfo


@admin.register(ClubInfo)
class ClubInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'address', 'phone', 'email')
    list_per_page = 20
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slogan', 'description')
        }),
        ('Контакты', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Статистика профиля', {
            'fields': ('profile_games', 'profile_hours', 'profile_tournaments')
        }),
    )
