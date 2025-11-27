from django.contrib import admin
from .models import  Producto, Pedido, CustomUser



admin.site.register(CustomUser)
admin.site.register(Pedido)

class PedidoInline(admin.TabularInline):
    model = Pedido
    extra = 1
    readonly_fields = ('id_pedido', 'fecha_pedido')
    show_change_link = True

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre', 'precio', 'stock')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('precio',)
    ordering = ('id_producto',)
    readonly_fields = ('id_producto',)
    list_per_page = 4
    inlines = [PedidoInline]

    