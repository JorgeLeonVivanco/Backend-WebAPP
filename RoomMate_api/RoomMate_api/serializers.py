from rest_framework import serializers
from rest_framework.authtoken.models import Token
from RoomMate_api.models import *

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

class ClienteSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Cliente
        fields = "__all__"

class PropiedadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propiedades
        fields = '__all__'

def get_imagenes(self, obj):
        # Suponiendo que `imagenes` es un campo relacionado o una lista de nombres de archivos
        if obj.imagenes:
            # Construir una lista de URLs completas para las imágenes
            return [f"{settings.MEDIA_URL}{imagen}" for imagen in obj.imagenes]
        return []

class FiltroPropiedadesSerializer(serializers.Serializer):
    precio_min = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    precio_max = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    tipo_propiedad = serializers.CharField(required=False, max_length=100)
    servicios = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )

    def validate(self, data):
        """
        Validar que los filtros sean consistentes entre sí.
        Por ejemplo, si se proporciona precio_min, también se debe proporcionar precio_max y viceversa.
        """
        if data.get('precio_min') and not data.get('precio_max'):
            raise serializers.ValidationError("Debe proporcionar 'precio_max' si se proporciona 'precio_min'.")
        if data.get('precio_max') and not data.get('precio_min'):
            raise serializers.ValidationError("Debe proporcionar 'precio_min' si se proporciona 'precio_max'.")
        return data