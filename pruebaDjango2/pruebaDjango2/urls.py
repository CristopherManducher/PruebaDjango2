
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from pruebaDjangoApp2 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.suplementos, name='suplementos'),
    path('suplemento/<int:suplemento_id>/', views.suplemento_detalle, name='suplemento_detalle')

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    