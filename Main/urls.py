from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Кастомные обработчики ошибок
handler400 = 'Main.views.custom_bad_request'
handler403 = 'Main.views.custom_permission_denied'
handler404 = 'Main.views.custom_page_not_found'
handler500 = 'Main.views.custom_server_error'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Главные страницы
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('profile/', views.profile_view, name='profile'),
    path('hall-map/', views.hall_map_view, name='hall_map'),

    # Приложения
    path('users/', include('Users.urls')),
    path('services/', include('services.urls')),
    path('tournaments/', include('tournaments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)