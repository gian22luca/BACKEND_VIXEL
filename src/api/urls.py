from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'productoView', views.ProductoViewSet, basename='producto')
router.register(r'pedidoItemView', views.PedidoItemViewSet, basename='pedidoItem')


urlpatterns = [
    path('', views.inicio , name='inicio' ),
    path('info/', views.api_info),
    path('usuarios/', views.CustomUserAPIView.as_view()),
    path('productos/', views.ProductoAPIView.as_view()),
    path('pedidos/', views.PedidoAPIView.as_view()),
    path('usuarios/<int:pk>/', views.CustomUserDetalleAPIView.as_view()),
    path('productos/<int:pk>/', views.ProductoDetalleAPIView.as_view()),
    path('pedidos/<int:pk>/', views.PedidoDetalleAPIView.as_view()),
   
 
]

urlpatterns += router.urls