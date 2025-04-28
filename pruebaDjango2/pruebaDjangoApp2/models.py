from django.db import models

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
    
