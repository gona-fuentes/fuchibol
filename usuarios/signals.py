# usuarios/signals.py
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def enviar_correo_bienvenida(sender, instance, created, **kwargs):
    if created:  # Solo cuando se crea un usuario nuevo
        asunto = "¡Bienvenido a Fuchiapp!"
        mensaje = f"Hola {instance.first_name or instance.username},\n\n" \
                  "Gracias por registrarte en Fuchiapp. Ahora puedes reservar canchas y gestionar tus reservas.\n\n" \
                  "¡Disfruta jugando!"
        remitente = settings.DEFAULT_FROM_EMAIL
        destinatario = [instance.email]

        if instance.email:  # Verificamos que el usuario tenga correo
            send_mail(
                asunto,
                mensaje,
                remitente,
                destinatario,
                fail_silently=False,
            )
