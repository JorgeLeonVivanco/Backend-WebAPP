from django.shortcuts import render
from django.db.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from RoomMate_api.serializers import *
from RoomMate_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny

class ClienteAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        clientes = Cliente.objects.filter(user__is_active=True).order_by("id")
        lista = ClienteSerializer(clientes, many=True).data
        return Response(lista, status=200)


class ClienteView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # Permite acceso sin autenticación
    
    def get(self, request, *args, **kwargs):
        cliente = get_object_or_404(Cliente, id=request.GET.get("id"))
        cliente = ClienteSerializer(cliente, many=False).data
        return Response(cliente, status=200)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        
        if user_serializer.is_valid():
            # Extraer datos del request
            role = request.data.get("rol")
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            email = request.data.get("email")
            password = request.data.get("password")
            
            # Validar existencia del usuario/email
            if User.objects.filter(email=email).exists():
                return Response({"message": f"El email {email} ya está registrado."}, status=400)
            
            # Crear usuario
            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            user.set_password(password)
            user.save()
            
            # Asignar grupo
            group, _ = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            
            # Crear perfil de cliente
            cliente = Cliente.objects.create(
                user=user,
                telefono=request.data.get("telefono", ""),
                rol=role
            )
            
            return Response({"cliente_created_id": cliente.id}, status=201)

        return Response(user_serializer.errors, status=400)


class ClienteViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def put(self, request, *args, **kwargs):
        if "id" not in request.data:
            raise ValidationError({"id": "Este campo es requerido."})
        
        cliente = get_object_or_404(Cliente, id=request.data["id"])
        cliente.telefono = request.data.get("telefono", cliente.telefono)
        cliente.save()
        
        # Actualizar datos del usuario
        user = cliente.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        if request.data.get("password"):
            user.set_password(request.data["password"])
        user.save()
        
        cliente_serializado = ClienteSerializer(cliente, many=False).data
        return Response(cliente_serializado, status=200)
    
    def delete(self, request, *args, **kwargs):
        cliente = get_object_or_404(Cliente, id=request.GET.get("id"))
        try:
            cliente.user.delete()
            return Response({"details": "Cliente eliminado"}, status=200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, status=400)
