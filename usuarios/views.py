from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroUsuario, PerfilForm
from .models import Perfil
from canchas.models import Reserva

def index(request):
    """Página principal. Si está logueado, muestra opciones extendidas y reservas activas"""
    reservas = []
    if request.user.is_authenticated:
        reservas = Reserva.objects.filter(
            usuario=request.user, estado="Reservada"
        ).order_by("fecha", "hora_inicio")
    return render(request, "usuarios/index.html", {"reservas": reservas})

def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroUsuario(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("index")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistroUsuario()
    return render(request, "usuarios/registrar.html", {"form": form})

@login_required(login_url='login')
def perfil(request):
    """Vista del perfil de usuario (solo para mostrar información)"""
    usuario = request.user
    perfil = usuario.perfil
    reservas = Reserva.objects.filter(usuario=usuario, estado="Reservada").order_by("fecha", "hora_inicio")
    return render(request, "usuarios/dashboard_usuario.html", {
        "usuario": usuario,
        "perfil": perfil,
        "reservas": reservas,
    })

@login_required(login_url='login')
def dashboard_usuario(request):
    """Mantener por compatibilidad, puede redirigir a perfil"""
    return redirect('perfil')
