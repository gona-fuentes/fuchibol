from django.contrib import admin
from .models import Cancha, Reserva


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ubicacion", "cantidad_jugadores", "precio_por_hora")
    search_fields = ("nombre", "ubicacion")
    list_filter = ("cantidad_jugadores",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("cancha", "usuario", "fecha", "hora_inicio", "hora_fin", "estado")
    list_filter = ("fecha", "estado", "cancha")
    search_fields = ("usuario__username", "cancha__nombre")
    ordering = ("-fecha", "-hora_inicio")
