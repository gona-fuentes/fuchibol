from django.urls import path
from . import views

urlpatterns = [
    path("", views.listar_canchas, name="listar_canchas"),
    path("reservar/<int:cancha_id>/", views.reservar_cancha, name="reservar_cancha"),
    path("dashboard/", views.dashboard_canchas, name="dashboard_canchas"),
    path("cancelar/<int:reserva_id>/", views.cancelar_reserva, name="cancelar_reserva"),






    path("admin/", views.dashboard_admin, name="dashboard_admin"),
    path("admin/editar/<int:cancha_id>/", views.editar_cancha, name="editar_cancha"),
    path("admin/eliminar/<int:cancha_id>/", views.eliminar_cancha, name="eliminar_cancha"),
    path("admin/cancelar/<int:reserva_id>/", views.cancelar_reserva_admin, name="cancelar_reserva_admin"),
    path('reservas/completar/<int:id>/', views.completar_reserva_admin, name='completar_reserva_admin'),



]
