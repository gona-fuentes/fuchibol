from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    celular = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', message="Ingresa solo 8 dígitos")],
        blank=True
    )
    instagram = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Instagram",
        help_text="Opcional: tu usuario de Instagram"
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"

# Signal para crear perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)
