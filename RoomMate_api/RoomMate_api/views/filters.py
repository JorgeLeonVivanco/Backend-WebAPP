import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Propiedades
from ..serializers import PropiedadesSerializer, FiltroPropiedadesSerializer

class FilterPropiedadesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Validar los filtros
        filter_serializer = FiltroPropiedadesSerializer(data=request.GET)
        if filter_serializer.is_valid():
            filters = filter_serializer.validated_data
        else:
            return Response(filter_serializer.errors, status=400)

        # Inicializar la consulta de propiedades
        propiedades = Propiedades.objects.all()

        # Aplicar los filtros de precio y tipo de propiedad
        if filters.get('precio_min'):
            propiedades = propiedades.filter(precio__gte=filters['precio_min'])
        if filters.get('precio_max'):
            propiedades = propiedades.filter(precio__lte=filters['precio_max'])
        if filters.get('tipo_propiedad'):
            propiedades = propiedades.filter(tipo_propiedad__icontains=filters['tipo_propiedad'])

        # Filtrar por servicios
        if filters.get('servicios'):
            # Verificar si el parámetro 'servicios' es una cadena separada por comas
            if isinstance(filters['servicios'], str):
                servicios_list = [servicio.strip() for servicio in filters['servicios'].split(',')]
            else:
                servicios_list = filters['servicios']

            print(f"Servicios recibidos para filtrar: {servicios_list}")

            # Filtrar propiedades que tienen al menos uno de los servicios seleccionados
            propiedades_filtradas = []
            for propiedad in propiedades:
                try:
                    # Convertir 'servicios_json' de la propiedad en una lista de valores
                    servicios_propiedad = json.loads(propiedad.servicios_json)

                    # Verificar si al menos uno de los servicios seleccionados está presente
                    if any(servicio in servicios_propiedad for servicio in servicios_list):
                        propiedades_filtradas.append(propiedad)

                except json.JSONDecodeError:
                    print(f"Error al procesar JSON en la propiedad {propiedad.id}")

            propiedades = propiedades_filtradas  # Asignar las propiedades filtradas

        print(f"Propiedades después del filtro: {[propiedad.id for propiedad in propiedades]}")

        # Serializar las propiedades filtradas
        serializer = PropiedadesSerializer(propiedades, many=True)
        return Response(serializer.data)
