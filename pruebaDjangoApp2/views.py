from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from pruebaDjangoApp2.models import Suplementos, Categoria, Carrito, ItemCarrito
from datetime import datetime

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
    
    # Si el usuario está autenticado, usar su carrito
    if request.user.is_authenticated:
        # Obtener el carrito activo más reciente del usuario
        carrito = Carrito.objects.filter(usuario=request.user, activo=True).order_by('-fecha_creacion').first()
        if not carrito:
            carrito = Carrito.objects.create(usuario=request.user)
    else:
        # Si no está autenticado, usar el carrito de la sesión
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
        item.cantidad += 1
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
    
    # Aquí iría la lógica para procesar la compra
    # Por ahora solo mostraremos un mensaje de éxito
    messages.success(request, '¡Compra realizada con éxito!')
    carrito.activo = False  # Desactivamos el carrito actual
    return redirect('suplementos')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Si hay un carrito en la sesión, lo asignamos al usuario
            carrito_id = request.session.get('carrito_id')
            if carrito_id:
                carrito = Carrito.objects.get(id=carrito_id)
                carrito.usuario = user
                carrito.save()
                del request.session['carrito_id']
            
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login.html')
