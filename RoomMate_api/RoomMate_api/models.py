from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


class Cliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rol = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Perfil del cliente: {self.user.first_name}"


class Propiedades(models.Model):
    id = models.BigAutoField(primary_key=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    habitaciones = models.CharField(max_length=255, null=True, blank=True)
    capacidad = models.CharField(max_length=255, null=True, blank=True)
    precio = models.CharField(max_length=255, null=True, blank=True)
    servicios_json = models.TextField(null=True, blank=True)
    sanitarios = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    estados = models.CharField(max_length=255, null=True, blank=True)
    imagenes = models.JSONField(default=list)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)  # Relación con Cliente
    # Nuevos campos añadidos
    tipo_propiedad = models.CharField(max_length=255, null=True, blank=True)  # Ej. "Apartamento", "Casa", etc.
    comentarios = models.JSONField(default=list)  # Este campo almacena una lista de comentarios
    calificacion = models.IntegerField(null=True, blank=True)  # Calificación de 1 a 10

    def __str__(self):
        return f"Propiedad: {self.direccion}, capacidad: {self.capacidad}"
