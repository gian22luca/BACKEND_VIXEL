from rest_framework import serializers
from .models import CustomUser, Producto, Pedido, PedidoItem
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

def validar_caracteres_alfebeticos(value):
            """Validador para solo alfanuméricos"""
            import re
            if not re.match(r'^[a-zA-Z0-9\s]+$', value):
                raise serializers.ValidationError(
                    'Solo se permiten letras, números y espacios.'
                    )
            return value


class PedidoItemSerializer(serializers.ModelSerializer):
    # si querés incluir info del producto:
    nombre_producto = serializers.CharField(source='producto.nombre', read_only=True)
    precio_producto = serializers.DecimalField(
        source='producto.precio', max_digits=10, decimal_places=2, read_only=True
    )
    archivo = serializers.CharField(source='producto.archivo', read_only=True)

    class Meta:
        model = PedidoItem
        fields = ('id', 'producto', 'cantidad',
                  'nombre_producto', 'precio_producto', 'archivo') 
        

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'is_staff', 'phone', 'address', 'birth_date']
        read_only_fields = ['id_usuario']
        validators = [validar_caracteres_alfebeticos]
       


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id_producto', 'nombre', 'descripcion', 'precio', 'stock', 'archivo']
        nombre = serializers.CharField(validators = [validar_caracteres_alfebeticos])
        descipcion = serializers.CharField(validators = [validar_caracteres_alfebeticos])                                
        read_only_fields = ['id_producto']

    def validate_precio(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value
    
    

class PedidoSerializer(serializers.ModelSerializer):
    items = PedidoItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido 
        fields = ['id_pedido', 'usuario', 'fecha_pedido', 'estado', 'precio_total','items']
        read_only_fields = ['id_pedido', 'fecha_pedido','usuario']
    def validar_precio_total(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio total no puede ser negativo.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
       
        token['email'] = user.email
        token['phone'] = getattr(user, 'phone', None) 
        token['is_staff'] = user.is_staff
        return token      
    

class ContactoSerializer(serializers.Serializer):
    fist_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)    
    message = serializers.CharField()   