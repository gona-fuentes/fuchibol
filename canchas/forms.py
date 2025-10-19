from django import forms
from .models import Cancha

class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = ['nombre', 'ubicacion', 'cantidad_jugadores', 'precio_por_hora', 'descripcion', 'imagen']
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }
