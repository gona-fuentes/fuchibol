from django.contrib import admin
from django.urls import path, include
from usuarios import views as usuarios_views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('admin/', admin.site.urls),

    # Página inicial
    path('', usuarios_views.index, name='index'),

    # App usuarios
    path('usuarios/', include('usuarios.urls')),

    # App canchas
    path('canchas/', include(('canchas.urls', 'canchas'), namespace='canchas')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
