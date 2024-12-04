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
from rest_framework.parsers import JSONParser
import json
import requests

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
            
            # Convertir servicios de cadena JSON a lista
            if propiedad.servicios_json:
                propiedad_data['servicios_json'] = json.loads(propiedad.servicios_json)
            
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
                cliente=cliente , # Asociar el cliente al crear la propiedad
                latitud=request.data.get("latitud", None),  # Aceptar latitud
                longitud=request.data.get("longitud", None),  # Aceptar longitud
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
        propiedad.latitud = request.data.get("latitud", propiedad.latitud)  # Editar latitud si se proporciona
        propiedad.longitud = request.data.get("longitud", propiedad.longitud)  # Editar longitud si se proporciona
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
            propiedad.servicios_json = json.loads(propiedad.servicios_json)
            
            # Obtener datos del propietario
            propietario = propiedad.cliente.user  # Asumiendo que cliente.user es el propietario
            propietario_data = {
                "nombre": propietario.get_full_name(),
                "correo": propietario.email,
                "telefono": propiedad.telefono,  # Cambiar según tu modelo
            }
            
            # Convertir rutas relativas de las imágenes a URLs completas
            data = serializer.data
            data["propietario"] = propietario_data
            if "imagenes" in data and data["imagenes"]:
                data["imagenes"] = [
                    f"{request.scheme}://{request.get_host()}/{settings.MEDIA_URL}{img}" for img in data["imagenes"]
                ]
            
            return Response(data, status=status.HTTP_200_OK)
        except Propiedades.DoesNotExist:
            return Response({'error': 'Propiedad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


class AutocompletarDireccionView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', '').strip()  # Obtener la cadena de búsqueda y eliminar espacios adicionales
        
        if not query:
            return Response({"error": "No se proporcionó una consulta"}, status=status.HTTP_400_BAD_REQUEST)

        # Llamada a la API de Nominatim (OpenStreetMap)
        nominatim_url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': query,
            'format': 'json',
            'addressdetails': 1,  # Obtener detalles completos de la dirección
            'limit': 5,  # Limitar los resultados a las primeras 5 sugerencias
        }

        headers = {
            'User-Agent': 'RoomMate/1.0 (davidcbd17@gmail.com.com)'  # Agrega tu nombre de aplicación y un correo de contacto
        }

        try:
            response = requests.get(nominatim_url, params=params, headers=headers)
            response.raise_for_status()  # Verifica si la respuesta fue exitosa (status 2xx)
            data = response.json()

            if not data:
                return Response({"error": "No se encontraron direcciones."}, status=status.HTTP_404_NOT_FOUND)

            sugerencias = [
                {
                    'nombre': item.get('display_name', ''),
                    'lat': item.get('lat', ''),
                    'lon': item.get('lon', ''),
                }
                for item in data
            ]

            return Response(sugerencias, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Error en la conexión con el servicio de Nominatim: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
    def delete(self, request, propiedad_id, usuario, comentario_texto, *args, **kwargs):
        try:
            # Obtener la propiedad
            propiedad = Propiedades.objects.get(id=propiedad_id)
            
            # Verificar si los comentarios existen en la propiedad
            if not propiedad.comentarios:
                return Response({'error': 'No hay comentarios para eliminar'}, status=status.HTTP_404_NOT_FOUND)
            
            # Filtrar el comentario específico del usuario y texto proporcionado
            comentarios_actualizados = [
                com for com in propiedad.comentarios 
                if not (com['usuario'] == usuario and com['texto'] == comentario_texto)
            ]
            
            # Verificar si el comentario fue encontrado y eliminado
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

#as