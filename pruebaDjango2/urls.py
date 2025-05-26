from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from pruebaDjangoApp2 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.suplementos, name='suplementos'),
    path('suplemento/<int:suplemento_id>/', views.suplemento_detalle, name='suplemento_detalle'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:suplemento_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/realizar-compra/', views.realizar_compra, name='realizar_compra'),
    path('login/', views.login_view, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    