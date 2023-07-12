# NOS VA A PERMITIR CONVERTIR LA DATA
from .models import *
from rest_framework import serializers

class TipoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProducto
        fields = '__all__'  

class ProductoSerializer(serializers.ModelSerializer):
    tipo = TipoProductoSerializer(read_only=True)
    class Meta:
        model = Producto
        fields = '__all__'


class TipoSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = '__all__'


class TipoHistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialCompra
        fields = '__all__'
