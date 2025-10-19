# ============================
# IMPORTACIONES
# ============================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.timezone import now
from django.conf import settings
from django.db import IntegrityError

from datetime import datetime, time

from .models import Cancha, Reserva
from .forms import CanchaForm

# ============================
# FUNCIONALIDADES DE USUARIO
# ============================

def listar_canchas(request):
    canchas = Cancha.objects.all()
    
    return render(request, "canchas/listar_canchas.html", {
        "canchas": canchas,
        "MEDIA_URL": settings.MEDIA_URL,  # Esto es clave para las imágenes
    })

# --- Reservar cancha ---
@login_required
def reservar_cancha(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    horas_disponibles = [f"{h:02d}:00" for h in range(18, 22)]  # 18:00 a 21:00

    if request.method == "POST":
        fecha = request.POST.get("fecha")
        hora_inicio = request.POST.get("hora_inicio")

        if fecha:
            fecha_reserva = datetime.strptime(fecha, "%Y-%m-%d").date()
            if fecha_reserva < now().date():
                messages.error(request, "⚠️ No puedes reservar en una fecha pasada.")
                return redirect("canchas:reservar_cancha", cancha_id=cancha.id)

        # Calcular hora de término
        hora_fin = None
        if hora_inicio:
            h, m = map(int, hora_inicio.split(":"))
            hora_fin = time((h + 1) % 24, m)

        # Buscar si hay reserva activa para esa cancha, fecha y hora
        reserva_activa = Reserva.objects.filter(
            cancha=cancha,
            fecha=fecha_reserva,
            hora_inicio=hora_inicio,
            estado="Reservada"
        ).first()

        if reserva_activa:
            messages.error(request, "⚠️ Esa hora ya está reservada, por favor elige otra.")
            return redirect("canchas:reservar_cancha", cancha_id=cancha.id)

        # Buscar reserva cancelada para esa cancha, fecha y hora
        reserva_cancelada = Reserva.objects.filter(
            cancha=cancha,
            fecha=fecha_reserva,
            hora_inicio=hora_inicio,
            estado="Cancelada"
        ).first()

        if reserva_cancelada:
            # Reactivar reserva cancelada actualizándola
            reserva_cancelada.usuario = request.user
            reserva_cancelada.hora_fin = hora_fin
            reserva_cancelada.estado = "Reservada"
            reserva_cancelada.save()

            # Enviar correo de reactivación
            send_mail(
                "Reserva reactivada",
                f"Hola {request.user.first_name}, tu reserva para la cancha {cancha.nombre} "
                f"el día {fecha_reserva} a las {hora_inicio} ha sido reactivada con éxito.",
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )

            messages.success(request, "✅ ¡La reserva ha sido reactivada con éxito!")
            return redirect("index")

        # Si no existe ninguna reserva, crear una nueva
        Reserva.objects.create(
            cancha=cancha,
            usuario=request.user,
            fecha=fecha_reserva,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado="Reservada",
        )

        # Enviar correo de confirmación
        send_mail(
            "Reserva confirmada",
            f"Hola {request.user.first_name}, tu reserva para la cancha {cancha.nombre} "
            f"el día {fecha_reserva} a las {hora_inicio} ha sido creada con éxito.",
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )

        messages.success(request, "✅ ¡La reserva ha sido creada con éxito!")
        return redirect("index")

    today = now().date().isoformat()
    return render(request, "canchas/reservar_cancha.html", {
        "cancha": cancha,
        "horas_disponibles": horas_disponibles,
        "today": today,
    })



# --- Dashboard de usuario (ver reservas) ---
@login_required
def dashboard_canchas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by("-fecha", "-hora_inicio")
    return render(request, "canchas/dashboard_canchas.html", {"reservas": reservas})


# --- Cancelar reserva (usuario) ---
@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)

    if reserva.estado == "Reservada":
        reserva.estado = "Cancelada"
        reserva.save()

        # Enviar correo al usuario
        send_mail(
            "Reserva cancelada",
            f"Hola {request.user.first_name}, tu reserva en la {reserva.cancha.nombre} "
            f"para el día {reserva.fecha} a las {reserva.hora_inicio} fue cancelada.",
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False,
        )

    return redirect("dashboard_usuario")


# ============================
# FUNCIONALIDADES ADMINISTRADOR
# ============================

# --- Dashboard admin (gestión canchas y reservas) ---
@staff_member_required(login_url='login')
def dashboard_admin(request):
    if not request.user.is_staff:
        return redirect('index')

    canchas = Cancha.objects.all()
    estado = request.GET.get('estado', '')
    
    reservas = Reserva.objects.filter(estado=estado).order_by("-fecha", "-hora_inicio") if estado \
               else Reserva.objects.all().order_by("-fecha", "-hora_inicio")

    if request.method == "POST":
        form = CanchaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("canchas:dashboard_admin")
    else:
        form = CanchaForm()

    return render(request, "canchas/dashboard_admin.html", {
        "canchas": canchas,
        "reservas": reservas,
        "form": form,
        "estado_filtrado": estado,
    })


# --- Editar cancha ---
@staff_member_required(login_url='login')
def editar_cancha(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)

    if request.method == "POST":
        form = CanchaForm(request.POST, instance=cancha)
        if form.is_valid():
            form.save()
            return redirect("canchas:dashboard_admin")
    else:
        form = CanchaForm(instance=cancha)

    return render(request, "canchas/editar_cancha.html", {
        "form": form,
        "cancha": cancha,
    })


# --- Eliminar cancha ---
@staff_member_required(login_url='login')
def eliminar_cancha(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)

    if request.method == "POST":
        cancha.delete()
        return redirect("canchas:dashboard_admin")

    return render(request, "canchas/eliminar_cancha.html", {"cancha": cancha})


# --- Cancelar reserva (admin) ---
@staff_member_required(login_url='login')
def cancelar_reserva_admin(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        reserva.estado = "Cancelada"
        reserva.save()

        # Enviar correo al usuario
        if reserva.usuario.email:
            asunto = f"Reserva cancelada: {reserva.cancha.nombre}"
            mensaje = (
                f"Hola {reserva.usuario.first_name or reserva.usuario.username},\n\n"
                f"Tu reserva para la cancha {reserva.cancha.nombre} el {reserva.fecha} "
                f"a las {reserva.hora_inicio} ha sido cancelada por el administrador.\n\n"
                "Si tienes dudas, responde a este correo."
            )
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [reserva.usuario.email],
                fail_silently=True,
            )

        messages.success(request, "Reserva cancelada correctamente.")
        return redirect("canchas:dashboard_admin")

    return redirect("canchas:dashboard_admin")


# --- Completar reserva (admin) ---
@staff_member_required(login_url='login')
def completar_reserva_admin(request, id):
    reserva = get_object_or_404(Reserva, id=id)
    reserva.estado = 'Completada'
    reserva.save()

    return redirect("canchas:dashboard_admin")

@staff_member_required(login_url='login')
def cancelar_reserva_admin(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST" and reserva.estado == "Reservada":
        reserva.estado = "Cancelada"
        reserva.save()

        # Enviar correo al usuario dueño de la reserva
        if reserva.usuario.email:
            send_mail(
                "Reserva cancelada por administrador",
                f"Hola {reserva.usuario.first_name or reserva.usuario.username},\n\n"
                f"Tu reserva en la  {reserva.cancha.nombre} para el día {reserva.fecha} "
                f"a las {reserva.hora_inicio} fue cancelada por un administrador.\n\n"
                "Si tienes alguna duda, puedes contactarnos.",
                settings.DEFAULT_FROM_EMAIL,
                [reserva.usuario.email],
                fail_silently=True,
            )

        messages.success(request, "Reserva cancelada correctamente.")
        return redirect("canchas:dashboard_admin")

    return redirect("canchas:dashboard_admin")