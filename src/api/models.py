from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.db.models import Sum, F

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    

    def __str__(self):
        return f"{self.username} ({self.email})"
    

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    id_producto = models.AutoField(primary_key=True, unique=True)
    archivo = models.FileField(upload_to='archivos/', null=True, blank=True)
    
    
    

    def __str__(self):
        return f"{self.id_producto} {self.nombre} {self.precio} {self.stock}{self.archivo}"
    
class Pedido(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='usuarios')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    id_pedido = models.AutoField(primary_key=True, unique=True)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        default='Pendiente',
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Enviado', 'Enviado'),
            ('Entregado', 'Entregado'),
            ('Cancelado', 'Cancelado')
        ]
    )
    def actualizar_precio_total(self):
        """
        Suma cantidad * precio de cada item del pedido y
        guarda el resultado en precio_total.
        """
        total = self.items.aggregate(
            total= Sum(
                F('cantidad') * F('producto__precio'),
                output_field= models.DecimalField(max_digits=10, decimal_places=2)
            )
        )['total'] or 0

        self.precio_total = total
        self.save(update_fields=['precio_total'])

    def __str__(self):
        return f"{self.id_pedido} {self.usuario} {self.fecha_pedido} {self.estado}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # después de guardar el item, recalcula el total del pedido
        self.pedido.actualizar_precio_total()

    def delete(self, *args, **kwargs):
        pedido = self.pedido
        super().delete(*args, **kwargs)
        # después de borrar el item, también recalcula
        pedido.actualizar_precio_total()

    def __str__(self):
        return f"Pedido {self.pedido.id_pedido} - Producto {self.producto} - Cantidad {self.cantidad}"