from django.contrib import admin
from pruebaDjangoApp2.models import Suplementos,Categoria

class SuplementosAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria' , 'descripcion' , 'precio' , 'disponibilidad' , 'oferta' , 'unidadesVendidas' , 'imagenes', 'ofertaPorcentaje']



admin.site.register(Suplementos, SuplementosAdmin)
admin.site.register(Categoria)

