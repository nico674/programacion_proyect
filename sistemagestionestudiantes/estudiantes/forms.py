from django import forms
from .models import Estudiante

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'apellido', 'documento', 'codigo', 'email']  # campos que quieres mostrar en el formulario
