from django.db import models


class Curso(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    profesor = models.CharField(max_length=200)
    fecha_inicio = models.DateField()

    def __str__(self):
        return self.nombre
