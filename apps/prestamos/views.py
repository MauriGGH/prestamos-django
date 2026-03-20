from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from apps.empleados.models import Empleado
from .models import Prestamo, Abono


def prestamo_detail(request, pk):
	"""Detalle de un préstamo con información del empleado y abonos recientes"""
	prestamo = get_object_or_404(Prestamo, pk=pk)
	empleado = prestamo.empleado
	puesto_actual = empleado.obtener_puesto_actual()

	# Últimos 5 abonos para mostrar en el detalle
	abonos_recientes = prestamo.abonos.all().order_by('-numero_abono')[:5]
	total_abonos = prestamo.abonos.count()

	context = {
		"prestamo": prestamo,
		"empleado": empleado,
		"puesto_actual": puesto_actual,
		"abonos_recientes": abonos_recientes,
		"total_abonos": total_abonos,
	}
	return render(request, "prestamos/prestamo_detail.html", context)


def prestamo_list(request):
	"""Lista préstamos con paginación y filtro por estado"""
	prestamos = Prestamo.objects.select_related("empleado").all().order_by("-fecha_solicitud", "-id")

	estado_filter = request.GET.get("estado", "")
	if estado_filter:
		prestamos = prestamos.filter(estado=estado_filter)

	items_por_pagina = 10
	paginator = Paginator(prestamos, items_por_pagina)
	numero_pagina = request.GET.get("page", 1)

	try:
		page_obj = paginator.page(numero_pagina)
	except:
		page_obj = paginator.page(1)

	estados = Prestamo.ESTADO_CHOICES

	query_params = ""
	if estado_filter:
		query_params += f"&estado={estado_filter}"

	context = {
		"page_obj": page_obj,
		"prestamos": page_obj.object_list,
		"paginator": paginator,
		"estados": estados,
		"estado_filter": estado_filter,
		"query_params": query_params,
	}
	return render(request, "prestamos/prestamo_list.html", context)


def prestamo_create(request):
	empleados = Empleado.objects.filter(activo=True).order_by("nombre")
	context = {"empleados": empleados}

	if request.method == "POST":
		prestamo = Prestamo(
			empleado_id=request.POST.get("empleado"),
			monto=request.POST.get("monto"),
			plazo_meses=request.POST.get("plazo_meses"),
			tasa_interes_mensual=request.POST.get("tasa_interes_mensual") or 1.00,
			estado=request.POST.get("estado") or "SOLICITADO",
		)

		try:
			prestamo.full_clean()
			prestamo.save()
			return redirect("prestamo_list")
		except ValidationError as exc:
			context["errors"] = exc.messages
			context["prestamo"] = prestamo

	return render(request, "prestamos/prestamo_form.html", context)


def prestamo_update(request, pk):
	prestamo = get_object_or_404(Prestamo, pk=pk)
	empleados = Empleado.objects.filter(activo=True).order_by("nombre")
	context = {"prestamo": prestamo, "empleados": empleados}

	if request.method == "POST":
		prestamo.empleado_id = request.POST.get("empleado")
		prestamo.monto = request.POST.get("monto")
		prestamo.plazo_meses = request.POST.get("plazo_meses")
		prestamo.tasa_interes_mensual = request.POST.get("tasa_interes_mensual") or prestamo.tasa_interes_mensual
		prestamo.estado = request.POST.get("estado") or prestamo.estado

		try:
			prestamo.full_clean()
			prestamo.save()
			return redirect("prestamo_list")
		except ValidationError as exc:
			context["errors"] = exc.messages

	return render(request, "prestamos/prestamo_form.html", context)


def prestamo_delete(request, pk):
	prestamo = get_object_or_404(Prestamo, pk=pk)

	if request.method == "POST":
		prestamo.delete()
		return redirect("prestamo_list")

	return render(request, "prestamos/prestamo_confirm_delete.html", {"prestamo": prestamo})


# ========== ACCIONES RÁPIDAS ==========

def prestamo_aprobar(request, pk):
	"""Cambiar estado de SOLICITADO a APROBADO y establecer fecha de aprobación"""
	prestamo = get_object_or_404(Prestamo, pk=pk)

	if prestamo.estado == "SOLICITADO":
		prestamo.estado = "APROBADO"
		prestamo.fecha_aprobacion = datetime.now().date()
		prestamo.save()

	return redirect("prestamo_list")


def prestamo_rechazar(request, pk):
	"""Cambiar estado de SOLICITADO a RECHAZADO"""
	prestamo = get_object_or_404(Prestamo, pk=pk)

	if prestamo.estado == "SOLICITADO":
		prestamo.estado = "RECHAZADO"
		prestamo.save()

	return redirect("prestamo_list")


def prestamo_liberar(request, pk):
	"""Cambiar estado de APROBADO a ACTIVO y establecer fechas de descuento"""
	prestamo = get_object_or_404(Prestamo, pk=pk)

	if prestamo.estado == "APROBADO":
		hoy = datetime.now().date()
		prestamo.fecha_inicio_descuento = hoy + timedelta(days=30)
		prestamo.fecha_fin_descuento = hoy + timedelta(days=30 * prestamo.plazo_meses)
		prestamo.estado = "ACTIVO"
		prestamo.save()

	return redirect("prestamo_list")


# ========== ABONOS ==========

def abono_crear(request, pk):
	"""
	Registrar un abono a un préstamo ACTIVO.
	GET  → muestra la vista previa del abono calculado.
	POST → confirma y guarda el abono.
	"""
	prestamo = get_object_or_404(Prestamo, pk=pk)

	# Validación: solo préstamos ACTIVO aceptan abonos
	if prestamo.estado != "ACTIVO":
		return redirect("prestamo_detail", pk=pk)

	# ── Calcular preview del abono (misma lógica que Abono.save) ──
	saldo_anterior = prestamo.saldo_actual
	monto_interes = saldo_anterior * (prestamo.tasa_interes_mensual / 100)
	monto_capital = prestamo.pago_fijo_capital
	monto_cobrado = monto_capital + monto_interes
	nuevo_saldo = saldo_anterior - monto_capital
	numero_siguiente = (prestamo.abonos.count() or 0) + 1
	concluye = nuevo_saldo <= 0

	context = {
		"prestamo": prestamo,
		"preview": {
			"saldo_anterior": saldo_anterior,
			"monto_interes": monto_interes,
			"monto_capital": monto_capital,
			"monto_cobrado": monto_cobrado,
			"nuevo_saldo": nuevo_saldo,
			"numero_siguiente": numero_siguiente,
			"concluye": concluye,
		},
	}

	if request.method == "POST":
		abono = Abono(prestamo=prestamo)
		abono.save()  # La lógica completa ya está en Abono.save()
		return redirect("prestamo_detail", pk=pk)

	return render(request, "prestamos/abono_form.html", context)


def abono_list(request, pk):
	"""Historial completo de abonos de un préstamo"""
	prestamo = get_object_or_404(Prestamo, pk=pk)
	abonos = prestamo.abonos.all().order_by("numero_abono")

	context = {
		"prestamo": prestamo,
		"abonos": abonos,
	}
	return render(request, "prestamos/abono_list.html", context)
