from django.db import models
from django.contrib.auth.models import User

class Cancha(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.CharField(max_length=200)
    cantidad_jugadores = models.PositiveIntegerField()
    precio_por_hora = models.CharField(
        max_length=20,
        help_text="Precio en CLP por 1 hora, ejemplo: $25.000"
    )
    imagen = models.ImageField(upload_to="canchas/", blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_jugadores} jugadores)"


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ("Reservada", "Reservada"),
        ("Cancelada", "Cancelada"),
    ]

    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Reservada")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cancha', 'fecha', 'hora_inicio')  # ❌ evita duplicados

    def cancelar(self):
        """Método para cancelar una reserva"""
        self.estado = "Cancelada"
        self.save()

    def clean(self):
        """Validación: horario entre 18:00 y 22:00 y máximo 1 hora"""
        from django.core.exceptions import ValidationError
        import datetime

        hora_min = datetime.time(18, 0)
        hora_max = datetime.time(22, 0)

        if not (hora_min <= self.hora_inicio < hora_max):
            raise ValidationError("La hora de inicio debe estar entre las 18:00 y 22:00.")

        if not (hora_min < self.hora_fin <= hora_max):
            raise ValidationError("La hora de término debe estar entre las 18:00 y 22:00.")

        inicio = datetime.datetime.combine(self.fecha, self.hora_inicio)
        fin = datetime.datetime.combine(self.fecha, self.hora_fin)
        duracion = fin - inicio

        if duracion.total_seconds() > 3600:
            raise ValidationError("La reserva no puede durar más de 1 hora.")
        if duracion.total_seconds() <= 0:
            raise ValidationError("La hora de término debe ser posterior a la de inicio.")

    def __str__(self):
        return f"{self.usuario.username} → {self.cancha.nombre} ({self.fecha} {self.hora_inicio}-{self.hora_fin}) [{self.estado}]"
