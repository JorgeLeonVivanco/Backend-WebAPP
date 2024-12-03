from django.shortcuts import render
from django.db.models import *
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

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.is_active:
            roles = user.groups.all()
            role_names = []
            for role in roles:
                role_names.append(role.name)

            # Si solo es un rol específico, asignamos el elemento 0
            if len(role_names) > 0:
                role_names = role_names[0]

            token, created = Token.objects.get_or_create(user=user)

            if role_names == 'Estudiante':
                cliente = Cliente.objects.filter(user=user).first()
                cliente_data = ClienteSerializer(cliente).data
                cliente_data["token"] = token.key
                cliente_data["rol"] = "Estudiante"
                return Response(cliente_data, status=status.HTTP_200_OK)
            
            if role_names == 'Propietario':
                cliente = Cliente.objects.filter(user=user).first()
                cliente_data = ClienteSerializer(cliente).data
                cliente_data["token"] = token.key
                cliente_data["rol"] = "Propietario"
                return Response(cliente_data, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_403_FORBIDDEN)


class Logout(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Encabezados recibidos:", request.headers)  # Imprime todos los encabezados
        print("Usuario autenticado:", request.user)       # Imprime el usuario autenticado
        user = request.user

        if not user.is_authenticated:
            return Response({'message': 'Usuario no autenticado'}, status=401)

        try:
            token = Token.objects.get(user=user)
            token.delete()
            print("Token eliminado correctamente.")
            return Response({'message': 'Sesión cerrada correctamente'}, status=200)
        except Token.DoesNotExist:
            return Response({'message': 'No se encontró un token activo'}, status=400)

