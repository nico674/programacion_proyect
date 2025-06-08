from django.db import models
from django.db import models

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    email = models.EmailField()

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.codigo})"

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Nota(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    calificacion = models.FloatField()

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura}: {self.calificacion}"
