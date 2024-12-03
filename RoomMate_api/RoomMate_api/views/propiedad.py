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
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from ..models import Propiedades
import json

class PropiedadesAll(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        propiedades = Propiedades.objects.all()
        propiedades_serializadas = []

        for propiedad in propiedades:
            propiedad_data = PropiedadesSerializer(propiedad).data
            # Construir las URLs completas para las imágenes
            if propiedad.imagenes:
                propiedad_data['imagenes'] = [
                    f"{request.scheme}://{request.get_host()}/{settings.MEDIA_URL}{img}" for img in propiedad.imagenes
                ]
            propiedades_serializadas.append(propiedad_data)

        return Response(propiedades_serializadas, status=200)



class PropiedadesView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        try:
            # Obtener el cliente asociado al usuario autenticado
            user = request.user
            cliente = Cliente.objects.filter(user=user).first()

            if not cliente:
                return Response({"detail": "Cliente no encontrado."}, status=status.HTTP_404_NOT_FOUND)

            # Crear la propiedad
            propiedad = Propiedades.objects.create(
                direccion=request.data.get("direccion", ""),
                habitaciones=request.data.get("habitaciones", ""),
                capacidad=request.data.get("capacidad", ""),
                precio=request.data.get("precio", ""),
                servicios_json=json.dumps(request.data.get("servicios_json", [])),  # Convertir a JSON
                sanitarios=request.data.get("sanitarios", ""),
                telefono=request.data.get("telefono", ""),
                estados=request.data.get("estados", ""),
                tipo_propiedad=request.data.get("tipo_propiedad",""),
                cliente=cliente  # Asociar el cliente al crear la propiedad
            )

            # Manejo de imágenes
            imagenes = []
            if 'imagenes' in request.FILES:
                for img in request.FILES.getlist('imagenes'):
                    ruta_imagen = f"imagenes_propiedades/{img.name}"
                    with open(f"{settings.MEDIA_ROOT}/{ruta_imagen}", 'wb+') as destination:
                        for chunk in img.chunks():
                            destination.write(chunk)
                    imagenes.append(ruta_imagen)

            propiedad.imagenes = imagenes  # Guardar rutas de las imágenes en JSONField
            propiedad.save()

            return Response({"message": "Propiedad registrada correctamente.", "id": propiedad.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    #Se tiene que modificar la parte de edicion y eliminar
class PropiedadViewEdit(generics.CreateAPIView):
    #permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        # iduser=request.data["id"]
        propiedad = get_object_or_404(Propiedades, id=request.data["id"])
        propiedad.direccion = request.data["direccion"]
        propiedad.habitaciones = request.data["habitaciones"]
        propiedad.capacidad = request.data["capacidad"]
        propiedad.precio = request.data["precio"]
        propiedad.servicios_json = json.dumps(request.data["servicios_json"])
        propiedad.sanitarios = request.data["sanitarios"]
        propiedad.telefono =  request.data["telefono"]
        propiedad.estados =  request.data["estados"]
        propiedad.tipo_propiedad = request.data["tipo_propiedad"]
        propiedad.save()
        temp = propiedad
        temp.direccion = request.data["direccion"]
        temp.capacidad = request.data["capacidad"]
        temp.save()
        propiedades = PropiedadesSerializer(propiedad, many=False).data

        return Response(propiedades,200)
    
    def delete(self, request, *args, **kwargs):
        propiedad = get_object_or_404(Propiedades, id=request.GET.get("id"))
        try:
            propiedad.delete()
            return Response({"details":"Propiedad eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)
        
class PropiedadDetailView(APIView):
    def get(self, request, id, *args, **kwargs):
        try:
            propiedad = Propiedades.objects.get(pk=id)
            serializer = PropiedadesSerializer(propiedad)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Propiedades.DoesNotExist:
            return Response({'error': 'Propiedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)