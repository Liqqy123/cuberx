from django.contrib import admin
from .models import Tournament


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'format', 'date', 'prize', 'slots', 'max_slots', 'is_featured')
    list_filter = ('game', 'format', 'is_online', 'is_featured')
    search_fields = ('title', 'game')
    ordering = ('date',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'game', 'format', 'date', 'prize')
        }),
        ('Места', {
            'fields': ('slots', 'max_slots', 'is_online', 'is_featured')
        }),
    )
