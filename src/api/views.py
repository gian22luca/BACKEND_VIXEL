from django.shortcuts import render
from django.http import HttpResponse , JsonResponse
from rest_framework.views import APIView
from .models import  Producto, Pedido, CustomUser, PedidoItem
from django.shortcuts import get_object_or_404
from .serializers import CustomUserSerializer, ProductoSerializer, PedidoSerializer, ContactoSerializer
from rest_framework.response import Response
from django.db.models.deletion import RestrictedError
from rest_framework import status
from django.db.models import Q
#Permisos
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from utils.permission import TienePermisoModelo
#Paginación
from rest_framework.pagination import PageNumberPagination
from utils.pagination import CustomPagination
#Documentacion
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Response as OpenAPIResponse

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, ProductoSerializer 
from rest_framework.viewsets import ModelViewSet
import logging
from django.core.mail import send_mail

logger = logging.getLogger('api_vixel')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




# Create your views here.
def inicio(request):
    mensaje = "<h1>¡Bienvenido a Vixel!</h1>"
    return HttpResponse(mensaje)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_info(request):
    """
        Información general de la API de Vixel.
    """
    """send_mail(
        subject="Acceso a la API de Vixel",
        message="Se ha accedido a la vista de información de la API.",
        from_email="vixel.ventas@gmail.com",
        recipient_list=["test@test.com"],
        fail_silently=False                
                        
    )"""
    response = {
        "message":"Bienvenido a la API de  Vixel",
        "version": "1.0"
    }
    return JsonResponse(response)


@api_view(['GET'])
def search_users_safe(request):
    query = request.GET.get('query','')

    users = CustomUser.objects.filter(
        Q(email__icontains=query) | Q(first_name__icontains=query)
    ).values('id','email')

    return Response({
        'count': users.count(),
        'result': list(users)
    })

class CustomUserAPIView(APIView):
    model = CustomUser
    permission_classes = [IsAuthenticated, IsAdminUser] 
    @swagger_auto_schema(
        operation_description="Obtener una lista de CustomUsers",
        responses={
            200: CustomUserSerializer(many=True),
            201: CustomUserSerializer,
            400: OpenAPIResponse(
                description="Error de validación",
                schema=CustomUserSerializer(many=True)
            ) 
        }
    )
    def get(self, request):
        customuser = CustomUser.objects.all()
        paginator =CustomPagination()
        paginated_queryset = paginator.paginate_queryset(customuser, request)
        CustomUser_serializer = CustomUserSerializer(customuser, many=True)
        return paginator.get_paginated_response(CustomUser_serializer.data)
    
    @swagger_auto_schema(
        operation_description="Crear un nuevo CustomUser",
        request_body=CustomUserSerializer,
        responses={
            201: CustomUserSerializer,
            400: "Error de validación"
        }
    )
    def post(self, request):
        CustomUser_serializer = CustomUserSerializer(data=request.data)
        if CustomUser_serializer.is_valid():
            CustomUser_serializer.save()
            return Response(CustomUser_serializer.data, status=201)
        return Response(CustomUser_serializer.errors, status=400)

class CustomUserDetalleAPIView(APIView):
    model = CustomUser
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Obtener un CustomUser por ID",
        responses={
            200: CustomUserSerializer,
            404: "CustomUser no encontrado"
        }
    )
    def get(self, request, pk):
        try:
            customuser = CustomUser.objects.get(pk=pk)
            CustomUser_serializer = CustomUserSerializer(customuser)
            return Response(CustomUser_serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "CustomUser no encontrado"}, status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
        operation_description="Actualizar un CustomUser por ID",
        request_body=CustomUserSerializer,
        responses={
            200: CustomUserSerializer,
            400: "Error de validación",
            404: "CustomUser no encontrado"
        }
    )
    def put(self, request, pk):
        try:
            customuser = CustomUser.objects.get(pk=pk)
            CustomUser_serializer = CustomUserSerializer(customuser, data=request.data)
            if CustomUser_serializer.is_valid():
                CustomUser_serializer.save()
                respuesta = {
                    "message": "CustomUser actualizado correctamente",
                    "CustomUser": CustomUser_serializer.data
                }
                return Response(CustomUser_serializer.data)
            return Response(CustomUser_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "CustomUser no encontrado"}, status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Eliminar un CustomUser por ID",
        responses={
            204: "CustomUser eliminado correctamente",
            404: "CustomUser no encontrado",
            400: "No se puede eliminar el CustomUser porque tiene pedidos asociados"
        }
    )
    def delete(self, request, pk):
        try:
            customuser = CustomUser.objects.get(pk=pk)
            customuser.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({"error": "CustomUser no encontrado"}, status.HTTP_404_NOT_FOUND)
        except RestrictedError:
            return Response({"error": "No se puede eliminar el CustomUser porque tiene pedidos asociados"}, status=status.HTTP_400_BAD_REQUEST)

class ProductoAPIView(APIView):
    model = Producto
    permission_classes = [ AllowAny ]
    @swagger_auto_schema(
        operation_description="Obtener una lista de productos",
        responses={
            200: ProductoSerializer(many=True),
            201: ProductoSerializer,
            400: "Error de validación"
        }
    )
    def get(self, request):
        logger.info("Obteniendo la lista de productos")
        producto = Producto.objects.all()
        paginator =CustomPagination()
        paginated_queryset = paginator.paginate_queryset(producto, request)
        producto_serializer = ProductoSerializer(producto, many=True)
        return paginator.get_paginated_response(producto_serializer.data) 
    @swagger_auto_schema(
        operation_description="Crear un producto",
        request_body=ProductoSerializer,
        responses={
            201: ProductoSerializer,
            400: "Error de validación"  
        }
    )
    def post(self, request):
        producto_serializer = ProductoSerializer(data=request.data)
        if producto_serializer.is_valid():
            producto_serializer.save()
            return Response(producto_serializer.data, status=status.HTTP_201_CREATED)
        return Response(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductoDetalleAPIView(APIView):
    model = Producto
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Obtener un producto por id",
        responses={
            200: ProductoSerializer,
            404: "Producto no encontrado"
        }
    )
    def get(self, request, pk):
        try:
            producto = Producto.objects.get(pk=pk)
            producto_serializer = ProductoSerializer(producto)
            return Response(producto_serializer.data)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado"}, status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
        operation_description="Actualizar un producto por ID",
        request_body=ProductoSerializer,
        responses={
            200: ProductoSerializer,
            400: "Error de validación",
            404: "Producto no encontrado"
        }
    )
    def put(self, request, pk):
        try:
            producto = Producto.objects.get(pk=pk)
            producto_serializer = ProductoSerializer(producto, data=request.data)
            if producto_serializer.is_valid():
                producto_serializer.save()
                respuesta = {
                    "message": "Producto actualizado correctamente",
                    "CustomUser": producto_serializer.data
                }
                return Response(respuesta,producto_serializer.data)
            return Response(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado"}, status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Eliminar un producto por ID",
        responses={
            204: "Producto eliminado correctamente",
            404: "Producto no encontrado",
            400: "No se puede eliminar el producto porque tiene pedidos asociados"
        }
    )
    def delete(self, request, pk):
        try:
            producto = Producto.objects.get(pk=pk)
            producto.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except RestrictedError:
            return Response({"error": "No se puede eliminar el producto porque tiene pedidos asociados"}, status=status.HTTP_400_BAD_REQUEST)
    
class PedidoAPIView(APIView):
    model = Pedido
    permission_classes = [IsAuthenticated, TienePermisoModelo]

    # GET: devolver carrito actual del usuario (solo estado CARRITO)
    def get(self, request):
        pedido = Pedido.objects.filter(usuario=request.user, estado='CARRITO').first()
        if not pedido:
            # si no hay carrito abierto devolvemos vacío o null
            return Response(None, status=status.HTTP_200_OK)

        pedido_serializer = PedidoSerializer(pedido)
        return Response(pedido_serializer.data, status=status.HTTP_200_OK)

    # POST: agregar producto al carrito (crear/usar pedido CARRITO)
    def post(self, request):
        id_producto = request.data.get('producto')
        cantidad = int(request.data.get('cantidad', 1))

        if not id_producto:
            return Response(
                {"producto": ["Este campo es requerido."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        producto = get_object_or_404(Producto, pk=id_producto)

        # 1) Buscar o crear el carrito abierto del usuario
        pedido, created = Pedido.objects.get_or_create(
            usuario=request.user,
            estado='CARRITO'
        )

        # 2) Buscar si ya existe una línea para ese producto
        item, item_created = PedidoItem.objects.get_or_create(
            pedido=pedido,
            producto=producto,
        )
        if item_created:
            item.cantidad = cantidad
        else:
            item.cantidad += cantidad  # sumar al carrito
        item.save()
        pedido.actualizar_precio_total()

        # 3) Devolver el pedido completo con sus items
        pedido_serializer = PedidoSerializer(pedido)
        return Response(pedido_serializer.data, status=status.HTTP_201_CREATED)
    
class PedidoDetalleAPIView(APIView):
    model = Pedido
    permission_classes = [IsAuthenticated,TienePermisoModelo]
    @swagger_auto_schema(
        operation_description="Obtener un pedido por ID",
        responses={
            200: PedidoSerializer,
            404: "Pedido no encontrado"
        }
    )
    def get(self, request, pk):
        try:
            pedido = Pedido.objects.get(pk=pk)
            pedido_serializer = PedidoSerializer(pedido)
            return Response(pedido_serializer.data)
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Actualizar un pedido por ID",
        request_body=PedidoSerializer,
        responses={
            200: PedidoSerializer,
            400: "Error de validación",
            404: "Pedido no encontrado"
        }
    )
    def put(self, request, pk):
        try:
            pedido = Pedido.objects.get(pk=pk)
            pedido_serializer = PedidoSerializer(pedido, data=request.data)
            if pedido_serializer.is_valid():
                pedido_serializer.save()
                respuesta = {
                    "message": "Pedido actualizado correctamente",
                    "CustomUser": pedido_serializer.data
                }
                return Response(respuesta,pedido_serializer.data)
            return Response(pedido_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
        operation_description="Eliminar un pedido por ID",
        responses={
            204: "Pedido eliminado correctamente",
            404: "Pedido no encontrado",
            400: "No se puede eliminar el pedido porque tiene productos asociados"
        }   
    )
    def delete(self, request, pk):
        try:
            pedido = Pedido.objects.get(pk=pk)
            pedido.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        

class ProductoViewSet(ModelViewSet):

    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, TienePermisoModelo]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, TienePermisoModelo]
        return super().get_permissions()
    
    def get_queryset(self):
        stock = self.request.query_params.get('stock', None)
        if stock is not None:
            return Producto.objects.filter(stock__gt=0)
        return super().get_queryset()
    
class PedidoItemViewSet(ModelViewSet):
    model = PedidoItem
    queryset = PedidoItem.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated, TienePermisoModelo]

