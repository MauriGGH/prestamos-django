from django.contrib import admin
from apps.prestamos.models import Prestamo, Abono, Empleado

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'monto', 'saldo_actual', 'plazo_meses', 'estado')
    list_filter = ('estado',)
    search_fields = ('empleado__nombre',)
    
    # Campos que el usuario no podrá editar manualmente
    readonly_fields = ['pago_fijo_capital', 'saldo_actual']
    
    # Diseño visual del formulario por secciones
    fieldsets = (
        ('Información del empleado', {
            'fields': ('empleado',)
        }),
        ('Detalle del prestamo', {
            # Mantenemos 'pago_fijo_capital' aquí para que no marque error y se muestre en pantalla
            'fields': ('monto', 'saldo_actual', 'plazo_meses', 'tasa_interes_mensual', 'pago_fijo_capital')
        }),
    )

@admin.register(Abono)
class AbonoAdmin(admin.ModelAdmin):
    list_display = (
        'prestamo', 'numero_abono', 'fecha', 'monto_capital', 
        'monto_interes', 'monto_cobrado', 'saldo_actual'
    )
    search_fields = ('prestamo__empleado__nombre',)

    def has_change_permission(self, request, obj=None):
        """Bloquea por completo la edición de un abono que ya fue guardado"""
        return False

    def get_readonly_fields(self, request, obj=None):
        """Define qué campos son de solo lectura dependiendo si es nuevo o ya existe"""
        if obj:
            # Si el abono ya existe en la base de datos, TODO es de solo lectura
            return [
                'prestamo', 'numero_abono', 'fecha', 'monto_capital',
                'monto_interes', 'monto_cobrado', 'saldo_actual'
            ]
        # Si se está creando un abono nuevo, el usuario solo elige el 'prestamo'
        return [
            'numero_abono', 'fecha', 'monto_capital', 'monto_interes',
            'monto_cobrado', 'saldo_actual'
        ]