from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Booking, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    fieldsets = UserAdmin.fieldsets + (
        ('Контактная информация', {
            'fields': ('phone',),
        }),
        ('Статистика', {
            'fields': ('profile_games', 'profile_hours', 'profile_tournaments'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Контактная информация', {
            'fields': ('email', 'phone'),
        }),
        ('Статистика', {
            'fields': ('profile_games', 'profile_hours', 'profile_tournaments'),
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pc_name', 'booking_date', 'booking_time', 'duration', 'status', 'total_price')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__username', 'pc_name')
    autocomplete_fields = ('user', 'services')
    list_editable = ('status',)
