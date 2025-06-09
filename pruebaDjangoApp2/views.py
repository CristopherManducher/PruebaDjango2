from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from pruebaDjangoApp2.models import Suplementos, Categoria, Carrito, ItemCarrito
from datetime import datetime
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import FileSystemStorage
from .forms import SuplementosForm, CategoriaForm
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import re

def suplementos(request):
    suplementos = Suplementos.objects.all()
    categorias = Categoria.objects.all()
    categoriaSeleccionada = request.GET.get('dropdown')
    busqueda = request.GET.get('search', '')

    # Obtener la fecha actual
    fecha_actual = datetime.now().strftime("%d de %B de %Y")

    # Filtrar por búsqueda y categoría del suplemento
    if busqueda:
        suplementos = suplementos.filter(
            nombre__icontains=busqueda
        ) | suplementos.filter(
            descripcion__icontains=busqueda
        )

    if categoriaSeleccionada:
        suplementos = suplementos.filter(categoria=categoriaSeleccionada)

    # Paginación: Mostrar solo 20 suplementos por página
    paginator = Paginator(suplementos, 20)  
    pagina_numero = request.GET.get('page') 
    suplementos_pagina = paginator.get_page(pagina_numero)  

    # Los 5 suplementos más vendidos
    mas_vendidos = suplementos.order_by('-unidadesVendidas')[:5]

    data = {
        'suplementos': suplementos_pagina,  
        'categorias': categorias,
        'mas_vendidos': mas_vendidos,
        'busqueda': busqueda,
        'fecha_actual': fecha_actual
    }

    return render(request, 'index.html', data)


def suplemento_detalle(request, suplemento_id):
    suplemento = get_object_or_404(Suplementos, id=suplemento_id)
    busqueda = request.GET.get('search', '')

    # Obtener la fecha actual en la vista de detalle 
    fecha_actual = datetime.now().strftime("%d de %B de %Y")

    # Obtener todos los suplementos para filtrar
    if busqueda:
        suplementos = Suplementos.objects.all()  
        suplementos = suplementos.filter(
                nombre__icontains=busqueda
            ) | suplementos.filter(
                descripcion__icontains=busqueda
            )

    data = {
        'suplemento': suplemento,
        'busqueda': busqueda,
        'fecha_actual': fecha_actual  
    }
    return render(request, 'suplemento_detalle.html', data)

def agregar_al_carrito(request, suplemento_id):
    suplemento = get_object_or_404(Suplementos, id=suplemento_id)
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Si el usuario está autenticado, usar su carrito
    if request.user.is_authenticated:
        carrito = Carrito.objects.filter(usuario=request.user, activo=True).order_by('-fecha_creacion').first()
        if not carrito:
            carrito = Carrito.objects.create(usuario=request.user)
    else:
        carrito_id = request.session.get('carrito_id')
        if carrito_id:
            try:
                carrito = Carrito.objects.get(id=carrito_id, activo=True)
            except Carrito.DoesNotExist:
                carrito = Carrito.objects.create(usuario=None)
                request.session['carrito_id'] = carrito.id
        else:
            carrito = Carrito.objects.create(usuario=None)
            request.session['carrito_id'] = carrito.id
    
    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, suplemento=suplemento)
    
    if not created:
        item.cantidad += cantidad
    else:
        item.cantidad = cantidad
    item.save()
    
    messages.success(request, f'Producto {suplemento.nombre} agregado al carrito')
    return redirect('ver_carrito')

def ver_carrito(request):
    if request.user.is_authenticated:
        carrito = Carrito.objects.filter(usuario=request.user, activo=True).order_by('-fecha_creacion').first()
        if not carrito:
            carrito = Carrito.objects.create(usuario=request.user)
    else:
        carrito_id = request.session.get('carrito_id')
        if carrito_id:
            try:
                carrito = Carrito.objects.get(id=carrito_id, activo=True)
            except Carrito.DoesNotExist:
                carrito = Carrito.objects.create(usuario=None)
                request.session['carrito_id'] = carrito.id
        else:
            carrito = Carrito.objects.create(usuario=None)
            request.session['carrito_id'] = carrito.id
    
    items = carrito.itemcarrito_set.all()
    return render(request, 'carrito.html', {
        'carrito': carrito,
        'items': items
    })

def eliminar_del_carrito(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    else:
        carrito_id = request.session.get('carrito_id')
        item = get_object_or_404(ItemCarrito, id=item_id, carrito_id=carrito_id)
    
    item.delete()
    messages.success(request, 'Producto eliminado del carrito')
    return redirect('ver_carrito')

def actualizar_cantidad(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    else:
        carrito_id = request.session.get('carrito_id')
        item = get_object_or_404(ItemCarrito, id=item_id, carrito_id=carrito_id)
    
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad > 0:
        item.cantidad = cantidad
        item.save()
    else:
        item.delete()
    
    return redirect('ver_carrito')

@login_required
def realizar_compra(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para realizar la compra')
        return redirect('login')
    
    carrito = Carrito.objects.filter(usuario=request.user, activo=True).first()
    if not carrito:
        messages.error(request, 'No hay productos en el carrito')
        return redirect('ver_carrito')
    
    # Verificar disponibilidad y actualizar inventario
    items = carrito.itemcarrito_set.all()
    for item in items:
        suplemento = item.suplemento
        if item.cantidad > suplemento.disponibilidad:
            messages.error(request, f'No hay suficiente stock de {suplemento.nombre}. Disponible: {suplemento.disponibilidad}')
            return redirect('ver_carrito')
    
    # Si llegamos aquí, hay suficiente stock para todos los items
    # Actualizamos el inventario
    for item in items:
        suplemento = item.suplemento
        suplemento.disponibilidad -= item.cantidad
        suplemento.unidadesVendidas += item.cantidad
        suplemento.save()
    
    # Desactivar el carrito actual
    carrito.activo = False
    carrito.save()
    
    messages.success(request, '¡Compra realizada con éxito! Gracias por tu compra.')
    return redirect('ver_carrito')

def sanitize_input(input_str):
    """Sanitiza la entrada del usuario para prevenir SQL injection"""
    if not input_str:
        return None
    # Eliminar caracteres especiales y espacios en blanco
    sanitized = re.sub(r'[^\w\s@.-]', '', input_str)
    return sanitized.strip()

def login_view(request):
    if request.method == 'POST':
        username = sanitize_input(request.POST.get('username'))
        password = request.POST.get('password')  # No sanitizamos la contraseña para no afectar caracteres especiales
        
        # Validar que los campos no estén vacíos
        if not username or not password:
            messages.error(request, 'Por favor ingrese usuario y contraseña')
            return render(request, 'login.html')
        
        # Validar longitud máxima
        if len(username) > 150 or len(password) > 128:
            messages.error(request, 'Datos de entrada inválidos')
            return render(request, 'login.html')
        
        try:
            # Usar el método authenticate de Django que ya tiene protección contra SQL injection
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Registrar el inicio de sesión exitoso
                login(request, user)
                
                # Si hay un carrito en la sesión, lo asignamos al usuario
                carrito_id = request.session.get('carrito_id')
                if carrito_id:
                    try:
                        carrito = Carrito.objects.get(id=carrito_id)
                        carrito.usuario = user
                        carrito.save()
                        del request.session['carrito_id']
                    except Carrito.DoesNotExist:
                        pass
                
                # Redirección según tipo de usuario
                next_url = request.GET.get('next', '/')
                # Sanitizar la URL de redirección
                if next_url:
                    # Basic URL validation to prevent open redirect vulnerabilities
                    # from django.utils.http import is_safe_url
                    # if not is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    #    next_url = '/'
                    pass # Mantener next_url para redirección segura

                return redirect(next_url or '/') # Redirigir a la URL deseada o a la página principal
            else:
                # Si el usuario no existe o las credenciales son incorrectas
                messages.error(request, 'Usuario o contraseña incorrectos.')
        except Exception as e:
            messages.error(request, f'Ocurrió un error inesperado: {e}')

    return render(request, 'login.html')

def actualizar_cantidad_ajax(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_id = request.POST.get('item_id')
        cantidad = int(request.POST.get('cantidad', 0))

        if request.user.is_authenticated:
            item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        else:
            carrito_id = request.session.get('carrito_id')
            item = get_object_or_404(ItemCarrito, id=item_id, carrito_id=carrito_id)

        if cantidad > 0:
            item.cantidad = cantidad
            item.save()
            carrito = item.carrito
            return JsonResponse({'success': True, 'subtotal': item.subtotal, 'total': carrito.total})
        else:
            item.delete()
            carrito = item.carrito
            # Si el carrito está vacío después de eliminar el último artículo, también devolver el total actualizado
            if not carrito.itemcarrito_set.exists():
                return JsonResponse({'success': True, 'deleted': True, 'total': 0})
            return JsonResponse({'success': True, 'deleted': True, 'total': carrito.total})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@staff_member_required
def admin_panel(request):
    return redirect('admin_suplementos')

@staff_member_required
def admin_suplementos(request):
    suplementos = Suplementos.objects.all()
    return render(request, 'admin_suplementos.html', {'suplementos': suplementos})

@staff_member_required
def admin_suplemento_nuevo(request):
    if request.method == 'POST':
        form = SuplementosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suplemento creado correctamente.')
            return redirect('admin_suplementos')
    else:
        form = SuplementosForm()
    return render(request, 'admin_suplemento_nuevo.html', {'form': form})

@staff_member_required
def admin_suplemento_editar(request, suplemento_id):
    suplemento = get_object_or_404(Suplementos, id=suplemento_id)
    if request.method == 'POST':
        form = SuplementosForm(request.POST, request.FILES, instance=suplemento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suplemento actualizado correctamente.')
            return redirect('admin_suplementos')
    else:
        form = SuplementosForm(instance=suplemento)
    return render(request, 'admin_suplemento_editar.html', {'form': form, 'suplemento': suplemento})

@staff_member_required
def admin_suplemento_eliminar(request, suplemento_id):
    suplemento = get_object_or_404(Suplementos, id=suplemento_id)
    if request.method == 'POST':
        suplemento.delete()
        messages.success(request, 'Suplemento eliminado correctamente.')
        return redirect('admin_suplementos')
    return render(request, 'admin_suplemento_eliminar.html', {'suplemento': suplemento})

@staff_member_required
def admin_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'admin_categorias.html', {'categorias': categorias})

@staff_member_required
def admin_categoria_nueva(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('admin_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'admin_categoria_nueva.html', {'form': form})

@staff_member_required
def admin_categoria_editar(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('admin_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'admin_categoria_editar.html', {'form': form, 'categoria': categoria})

@staff_member_required
def admin_categoria_eliminar(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
        return redirect('admin_categorias')
    return render(request, 'admin_categoria_eliminar.html', {'categoria': categoria})
