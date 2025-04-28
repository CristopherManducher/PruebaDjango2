from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from pruebaDjangoApp2.models import Suplementos, Categoria
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

    # Cálculo del descuento para todos los suplementos existentes
    for s in suplementos:
        if s.oferta and s.ofertaPorcentaje > 0:
            descuento = (s.precio * s.ofertaPorcentaje) / 100
            s.precio_descuento = s.precio - descuento
        else:
            s.precio_descuento = s.precio

    # Paginación: Mostrar solo 20 suplementos por página
    paginator = Paginator(suplementos, 20)  
    pagina_numero = request.GET.get('page') 
    suplementos_pagina = paginator.get_page(pagina_numero)  

    # Los 5 suplementos más vendidos
    mas_vendidos = suplementos.order_by('-unidadesVendidas')[:5]

    # Cálculo del descuento si es que hay para los suplementos más vendidos
    for mv in mas_vendidos:
        if mv.oferta and mv.ofertaPorcentaje > 0:
            descuento = (mv.precio * mv.ofertaPorcentaje) / 100
            mv.precio_descuento = mv.precio - descuento
        else:
            mv.precio_descuento = mv.precio

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
        
    if suplemento.oferta and suplemento.ofertaPorcentaje > 0:
        descuento = (suplemento.precio * suplemento.ofertaPorcentaje) / 100
        suplemento.precio_descuento = suplemento.precio - descuento
    else:
        suplemento.precio_descuento = suplemento.precio

    data = {
        'suplemento': suplemento,
        'busqueda': busqueda,
        'fecha_actual': fecha_actual  
    }
    return render(request, 'suplemento_detalle.html', data)
