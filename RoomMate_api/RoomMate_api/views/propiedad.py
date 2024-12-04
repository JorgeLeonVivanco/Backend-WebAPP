import os
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


#     #Se tiene que modificar la parte de edicion y eliminar
# class PropiedadViewEdit(generics.UpdateAPIView):
#     def put(self, request, *args, **kwargs):
#         try:
#             # Obtener la propiedad por ID
#             propiedad = get_object_or_404(Propiedades, id=request.data["id"])

#             # Actualizar los campos básicos de la propiedad
#             propiedad.direccion = request.data.get("direccion", propiedad.direccion)
#             propiedad.habitaciones = request.data.get("habitaciones", propiedad.habitaciones)
#             propiedad.capacidad = request.data.get("capacidad", propiedad.capacidad)
#             propiedad.precio = request.data.get("precio", propiedad.precio)
#             propiedad.servicios_json = json.dumps(request.data.get("servicios_json", json.loads(propiedad.servicios_json)))  # Convertir a JSON
#             propiedad.sanitarios = request.data.get("sanitarios", propiedad.sanitarios)
#             propiedad.telefono = request.data.get("telefono", propiedad.telefono)
#             propiedad.estados = request.data.get("estados", propiedad.estados)
#             propiedad.tipo_propiedad = request.data.get("tipo_propiedad", propiedad.tipo_propiedad)

#             # Manejo de nuevas imágenes
#             if 'imagenes' in request.FILES:
#                 imagenes_nuevas = []
#                 for img in request.FILES.getlist('imagenes'):
#                     ruta_imagen = f"imagenes_propiedades/{img.name}"
#                     with open(f"{settings.MEDIA_ROOT}/{ruta_imagen}", 'wb+') as destination:
#                         for chunk in img.chunks():
#                             destination.write(chunk)
#                     imagenes_nuevas.append(ruta_imagen)

#                 # Si ya existen imágenes, las añadimos a las nuevas
#                 if propiedad.imagenes:
#                     propiedad.imagenes.extend(imagenes_nuevas)
#                 else:
#                     propiedad.imagenes = imagenes_nuevas

#             # Guardar la propiedad actualizada
#             propiedad.save()

#             return Response({"message": "Propiedad actualizada correctamente.", "id": propiedad.id}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PropiedadViewEdit(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, id, *args, **kwargs):
        """
        Obtiene los detalles de una propiedad por su ID.
        """
        try:
            propiedad = get_object_or_404(Propiedades, id=id)
            # Serializar los datos de la propiedad
            propiedad_serializer = PropiedadesSerializer(propiedad)
            propiedad_data = propiedad_serializer.data

            # Construir las URLs completas para las imágenes si existen
            if propiedad.imagenes:
                propiedad_data['imagenes'] = [
                    f"{request.scheme}://{request.get_host()}/{settings.MEDIA_URL}{img}" for img in propiedad.imagenes
                ]
            
            # Aquí se debe convertir el 'servicios_json' en una lista de servicios para poder marcar en el formulario
            servicios = json.loads(propiedad.servicios_json)  # Convierte el JSON a lista
            propiedad_data['servicios_json'] = servicios  # Se asigna la lista de servicios al campo 'servicios_json'

            return Response(propiedad_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, *args, **kwargs):
        """
        Edita los datos de una propiedad existente.
        """
        try:
            # Obtener la propiedad por ID
            propiedad = get_object_or_404(Propiedades, id=id)

            # Actualizar los campos de la propiedad con los datos proporcionados
            propiedad.direccion = request.data.get("direccion", propiedad.direccion)
            propiedad.habitaciones = request.data.get("habitaciones", propiedad.habitaciones)
            propiedad.capacidad = request.data.get("capacidad", propiedad.capacidad)
            propiedad.precio = request.data.get("precio", propiedad.precio)
            propiedad.servicios_json = json.dumps(request.data.get("servicios_json", json.loads(propiedad.servicios_json)))  # Convertir los servicios de vuelta a JSON
            propiedad.sanitarios = request.data.get("sanitarios", propiedad.sanitarios)
            propiedad.telefono = request.data.get("telefono", propiedad.telefono)
            propiedad.estados = request.data.get("estados", propiedad.estados)
            propiedad.tipo_propiedad = request.data.get("tipo_propiedad", propiedad.tipo_propiedad)

            # Manejo de nuevas imágenes
            if 'imagenes' in request.FILES:
                imagenes = []
                for img in request.FILES.getlist('imagenes'):
                    ruta_imagen = f"imagenes_propiedades/{img.name}"
                    with open(f"{settings.MEDIA_ROOT}/{ruta_imagen}", 'wb+') as destination:
                        for chunk in img.chunks():
                            destination.write(chunk)
                    imagenes.append(ruta_imagen)
                propiedad.imagenes = imagenes

            # Guardar los cambios de la propiedad
            propiedad.save()

            return Response({"message": "Propiedad actualizada correctamente."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
class PropiedadDetailView(APIView):
    def get(self, request, id, *args, **kwargs):
        try:
            propiedad = Propiedades.objects.get(pk=id)
            serializer = PropiedadesSerializer(propiedad)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Propiedades.DoesNotExist:
            return Response({'error': 'Propiedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
class AgregarComentarioAPIView(APIView):
    def post(self, request, propiedad_id):
        try:
            # Obtener la propiedad
            propiedad = Propiedades.objects.get(id=propiedad_id)
           
            # Obtener datos del comentario desde la solicitud
            comentario_data = request.data.get('comentario', {})
            nuevo_comentario = {
                "usuario": comentario_data.get('usuario', 'Usuario desconocido'),
                "fecha": datetime.now().isoformat(),
                "texto": comentario_data.get('texto', '').strip()
            }
           
            # Actualizar la lista de comentarios de la propiedad
            comentarios = propiedad.comentarios or []  # Si es None, inicializar como lista vacía
            comentarios.append(nuevo_comentario)
            propiedad.comentarios = comentarios
            propiedad.save()
           
            # Devolver la propiedad actualizada
            serializer = PropiedadesSerializer(propiedad)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        except Propiedades.DoesNotExist:
            return Response({'error': 'Propiedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#asssss
 
class EditarComentarioAPIView(APIView):
    def put(self, request, id, *args, **kwargs):
        try:
            # Obtener la propiedad usando el id de la URL
            propiedad = Propiedades.objects.get(id=id)
 
            # Obtener el nombre del cliente (usuario)
            usuario = request.user.get_full_name()  # Asume que el nombre completo del usuario está asociado con la propiedad
 
            # Buscar el comentario del cliente por nombre
            comentario = None
            for com in propiedad.comentarios:
                if com['usuario'] == usuario:
                    comentario = com
                    break
 
            if comentario is None:
                return Response({'error': 'Comentario no encontrado para este usuario'}, status=status.HTTP_404_NOT_FOUND)
 
            # Actualizar el comentario con el nuevo texto
            comentario_data = request.data.get('comentario', {})
            comentario['texto'] = comentario_data.get('texto', comentario['texto']).strip()
 
            propiedad.save()
 
            # Retornar la propiedad con el comentario actualizado
            serializer = PropiedadesSerializer(propiedad)
            return Response(serializer.data, status=status.HTTP_200_OK)
 
        except Propiedades.DoesNotExist:
            return Response({'error': 'Propiedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
       
 
class EliminarComentarioAPIView(APIView):
    def delete(self, request, propiedad_id, usuario, *args, **kwargs):
        try:
            # Obtener la propiedad
            propiedad = Propiedades.objects.get(id=propiedad_id)
           
            # Verificar si los comentarios existen en la propiedad
            if not propiedad.comentarios:
                return Response({'error': 'No hay comentarios para eliminar'}, status=status.HTTP_404_NOT_FOUND)
           
            # Buscar y eliminar el comentario del usuario especificado
            comentarios_actualizados = [com for com in propiedad.comentarios if com['usuario'] != usuario]
           
            if len(comentarios_actualizados) == len(propiedad.comentarios):
                return Response({'error': 'Comentario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
           
            # Actualizar la propiedad con la lista de comentarios sin el comentario eliminado
            propiedad.comentarios = comentarios_actualizados
            propiedad.save()
 
            # Retornar la propiedad actualizada
            serializer = PropiedadesSerializer(propiedad)
            return Response(serializer.data, status=status.HTTP_200_OK)
       
        except Propiedades.DoesNotExist:
            return Response({'error': 'Propiedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
class ObtenerCoordenadas(APIView):
    """
    Esta vista devolverá las coordenadas (latitud, longitud) y el nombre de la dirección de una propiedad.
    """
 
    def get(self, request, id, *args, **kwargs):
        try:
            # Buscar la propiedad por ID
            propiedad = Propiedades.objects.get(id=id)
           
            # Extraer los datos relevantes
            coordenadas = {
                'nombre_direccion': propiedad.direccion,
                'latitud': propiedad.latitud,
                'longitud': propiedad.longitud
            }
 
            return Response(coordenadas, status=status.HTTP_200_OK)
 
        except Propiedades.DoesNotExist:
            return Response({'error': 'Propiedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
 