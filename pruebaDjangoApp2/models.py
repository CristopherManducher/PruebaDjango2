from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Categoria(models.Model):
    nombreCategoria = models.CharField(max_length=50)


    def __str__(self):
        return self.nombreCategoria


class Suplementos(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria,on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=1000)
    precio = models.IntegerField()
    disponibilidad = models.IntegerField()
    oferta = models.BooleanField()
    unidadesVendidas= models.IntegerField()
    imagenes = models.ImageField(upload_to='productos', null=True)
    ofertaPorcentaje = models.PositiveIntegerField(default=0)
    
    @property
    def precio_descuento(self):
        if self.oferta:
            return self.precio * (1 - self.ofertaPorcentaje / 100)
        return self.precio

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        if self.usuario:
            return f"Carrito de {self.usuario.username}"
        return f"Carrito de sesión {self.id}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.itemcarrito_set.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    suplemento = models.ForeignKey(Suplementos, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cantidad} x {self.suplemento.nombre}"

    @property
    def subtotal(self):
        if self.suplemento.oferta:
            return self.cantidad * self.suplemento.precio_descuento
        return self.cantidad * self.suplemento.precio
    
