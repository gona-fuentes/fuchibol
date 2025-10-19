from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class RegistroUsuario(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Nombre", max_length=30, required=True)
    last_name = forms.CharField(label="Apellido", max_length=30, required=True)
    celular = forms.CharField(max_length=8, required=False)
    instagram = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")  # campos del User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            # actualizar perfil creado automáticamente
            perfil, created = Perfil.objects.get_or_create(user=user)
            perfil.celular = self.cleaned_data.get("celular", "")
            perfil.instagram = self.cleaned_data.get("instagram", "")
            perfil.save()
        return user

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['celular', 'instagram']
        widgets = {
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de celular'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario de Instagram'}),
        }
