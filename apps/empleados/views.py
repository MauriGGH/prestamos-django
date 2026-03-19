from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Empleado, Puesto 

def empleado_list(request):
    # 1. Obtener todos los empleados inicialmente
    empleados = Empleado.objects.all().order_by("nombre")

    # 2. Capturar los filtros desde la URL (Ej. ?activo=si&puesto=2)
    activo_filter = request.GET.get("activo", "")
    puesto_filter = request.GET.get("puesto", "")

    # 3. Aplicar filtro por estado activo
    if activo_filter == "si":
        empleados = empleados.filter(activo=True)
    elif activo_filter == "no":
        empleados = empleados.filter(activo=False)

    # 4. Aplicar filtro por puesto actual (usando la relación del historial)
    if puesto_filter:
        empleados = empleados.filter(
            historial_puestos__puesto_id=puesto_filter,
            historial_puestos__fecha_fin__isnull=True # Solo el puesto activo actualmente
        )

    # 5. Configurar la paginación
    items_por_pagina = 10
    paginator = Paginator(empleados, items_por_pagina) # Paginator va con P mayúscula
    numero_pagina = request.GET.get("page", 1)
    
    try:
        page_obj = paginator.page(numero_pagina)
    except PageNotAnInteger:
        # Si la página no es un número, mostrar la primera
        page_obj = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página disponible
        page_obj = paginator.page(paginator.num_pages)

    # 6. Obtener puestos disponibles para llenar el <select> en tu HTML
    puestos = Puesto.objects.all().order_by("nombre")

    # 7. Conservar los parámetros de la URL para que la paginación no borre los filtros
    query_params = ""
    if activo_filter:
        query_params += f"&activo={activo_filter}"
    if puesto_filter:
        query_params += f"&puesto={puesto_filter}"

    # 8. Construir el contexto (Diccionario corregido)
    context = {
        "empleados": page_obj, # Enviamos los empleados ya paginados
        "page_obj": page_obj,
        "paginator": paginator,
        "puestos": puestos,
        "activo_filter": activo_filter,
        "puesto_filter": puesto_filter,
        "query_params": query_params
    }

    # 9. Retornar la respuesta al final (Tú lo tenías hasta arriba por error)
    return render(request, "empleados/empleado_list.html", context)

def empleado_detail(request, pk):
	empleado = get_object_or_404(Empleado, pk=pk)
	historial = empleado.historial_puestos.all().order_by("-fecha_inicio")
	prestamos = empleado.prestamos.all().order_by("-fecha_solicitud")
	context = {
		"empleado": empleado,
		"historial": historial,
		"prestamos": prestamos,
	}
	return render(request, "empleados/empleado_detail.html", context)

def empleado_create(request):
	if request.method == "POST":
		nombre = request.POST.get("nombre", "").strip()
		fecha_ingreso = request.POST.get("fecha_ingreso")
		activo = request.POST.get("activo", "").lower() in {"on", "true", "1",
			"si"}
		Empleado.objects.create(
			nombre=nombre,
			fecha_ingreso=fecha_ingreso,
			activo=activo,
		)
		return redirect("empleado_list")
	return render(request, "empleados/empleado_form.html")

def empleado_update(request, pk):
	empleado = get_object_or_404(Empleado, pk=pk)
	if request.method == "POST":
		empleado.nombre = request.POST.get("nombre", "").strip()
		empleado.fecha_ingreso = request.POST.get("fecha_ingreso")
		empleado.activo = request.POST.get("activo", "").lower() in {"on", "true",
			"1", "si"}
		empleado.save()
		return redirect("empleado_list")
	return render(request, "empleados/empleado_form.html", {"empleado": empleado})

def empleado_delete(request, pk):
	empleado = get_object_or_404(Empleado, pk=pk)
	if request.method == "POST":
		empleado.delete()
		return redirect("empleado_list")
	return render(request, "empleados/empleado_confirm_delete.html", {"empleado":
		empleado})
 
 