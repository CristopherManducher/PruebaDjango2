from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

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
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('carrito/actualizar-cantidad-ajax/', views.actualizar_cantidad_ajax, name='actualizar_cantidad_ajax'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/suplementos/', views.admin_suplementos, name='admin_suplementos'),
    path('admin-panel/suplementos/nuevo/', views.admin_suplemento_nuevo, name='admin_suplemento_nuevo'),
    path('admin-panel/suplementos/<int:suplemento_id>/editar/', views.admin_suplemento_editar, name='admin_suplemento_editar'),
    path('admin-panel/suplementos/<int:suplemento_id>/eliminar/', views.admin_suplemento_eliminar, name='admin_suplemento_eliminar'),
    path('admin-panel/categorias/', views.admin_categorias, name='admin_categorias'),
    path('admin-panel/categorias/nueva/', views.admin_categoria_nueva, name='admin_categoria_nueva'),
    path('admin-panel/categorias/<int:categoria_id>/editar/', views.admin_categoria_editar, name='admin_categoria_editar'),
    path('admin-panel/categorias/<int:categoria_id>/eliminar/', views.admin_categoria_eliminar, name='admin_categoria_eliminar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)    