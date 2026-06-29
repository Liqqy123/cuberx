from django.contrib import admin
from .models import ServiceItem


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = ('name', 'slug', 'category', 'price', 'period', 'is_featured', 'order')
    
    # Фильтры
    list_filter = ('category', 'is_featured')
    
    # Поиск
    search_fields = ('name', 'slug', 'description')
    
    # Сортировка
    ordering = ('order', 'name')
    
    # Поля только для чтения (slug генерируется автоматически)
    readonly_fields = ('slug',)
    
    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Цена и период', {
            'fields': ('price', 'period')
        }),
        ('Визуализация', {
            'fields': ('icon', 'image', 'is_featured', 'order')
        }),
    )
    
    # Поля, которые можно редактировать прямо в списке
    list_editable = ('price', 'is_featured', 'order')