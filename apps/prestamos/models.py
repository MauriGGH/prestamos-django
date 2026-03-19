from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.empleados.models import Empleado


# ==========================================
# MODELO PRÉSTAMO
# ==========================================
class Prestamo(models.Model):
    empleado = models.ForeignKey(
        Empleado, 
        on_delete=models.PROTECT,
        related_name='prestamos'
    )
    
    monto = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    plazo_meses = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )
    
    fecha_solicitud = models.DateField(
        auto_now_add=True, 
        help_text='Fecha de solicitud del préstamo'
    )
    fecha_aprobacion = models.DateField(
        null=True, blank=True, 
        help_text='Fecha de aprobación del préstamo'
    )
    fecha_inicio_descuento = models.DateField(
        null=True, blank=True,
        help_text='Fecha de inicio de los descuentos en nómina'
    )
    fecha_fin_descuento = models.DateField(
        null=True, blank=True, 
        help_text='Fecha de fin de los descuentos en nómina'
    )
    
    tasa_interes_mensual = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=1.00, validators=[MinValueValidator(0)], 
        help_text='Tasa de interés mensual en porcentaje'
    )
    
    pago_fijo_capital = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text='Pago fijo de capital mensual'
    )
    saldo_actual = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text='Saldo pendiente del préstamo'
    )
    
    ESTADO_CHOICES = [
        ('SOLICITADO', 'Solicitado'),
        ('APROBADO', 'Aprobado'),
        ('ACTIVO', 'Activo'),
        ('CONCLUIDO', 'Concluido'),
        ('RECHAZADO', 'Rechazado'),
    ]
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES,
        default='SOLICITADO'
    )

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Préstamo de {self.empleado.nombre} por {self.monto:.2f} a {self.plazo_meses} meses - Estado: {self.estado}"

    def calcular_monto_maximo(self):
        from apps.empleados.models import HistorialPuesto
        historial_actual = HistorialPuesto.objects.filter(
            empleado=self.empleado,
            fecha_fin__isnull=True
        ).first()
        if historial_actual:
            return historial_actual.puesto.sueldo * 6
        return 0 

    def puede_solicitar_prestamo(self):
        if not self.empleado:
            return False, "El préstamo debe estar asociado a un empleado."
            
        puede_solicitar, mensaje = self.empleado.puede_solicitar_prestamo(excluir_prestamo_id=self.pk)
        if not puede_solicitar:
            return False, mensaje
            
        monto_maximo = self.calcular_monto_maximo()
        if self.monto > monto_maximo:
            return False, f"El monto solicitado excede el máximo permitido de ${monto_maximo:.2f} basado en su puesto actual."
            
        return True, "Puede solicitar el préstamo."

    def clean(self):
        if not self.pk or self.estado == 'SOLICITADO':
            puede_solicitar, mensaje = self.puede_solicitar_prestamo()
            if not puede_solicitar:
                raise ValidationError(mensaje)
                
        if self.fecha_aprobacion and self.fecha_solicitud:
            if self.fecha_aprobacion < self.fecha_solicitud:
                raise ValidationError('La fecha de aprobación no puede ser anterior a la fecha de solicitud.')

    def save(self, *args, **kwargs):
        self.clean()
        if not self.pago_fijo_capital and self.monto and self.plazo_meses:
            self.pago_fijo_capital = self.monto / self.plazo_meses
        if not self.pk:
            self.saldo_actual = self.monto
        super().save(*args, **kwargs)


# ==========================================
# MODELO ABONO 
# ==========================================
class Abono(models.Model):
    prestamo = models.ForeignKey(
        Prestamo, 
        on_delete=models.CASCADE,
        related_name='abonos'
    )
    numero_abono = models.PositiveIntegerField(
        help_text='Número secuencial del abono', 
        default=1
    )
    fecha = models.DateField(
        auto_now_add=True, 
        help_text='Fecha del abono'
    )
    monto_capital = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, help_text='Monto del abono aplicado a capital'
    )
    monto_interes = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, help_text='Monto del abono aplicado a intereses'
    )
    monto_cobrado = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, help_text='Monto total cobrado en este abono'
    )
    saldo_actual = models.DecimalField(
        max_digits=12, decimal_places=2, 
        default=0, help_text='Saldo restante del préstamo después de este abono'
    )

    def __str__(self):
        # Le agregué este método rápido para que se vea bonito en el panel de administrador
        return f"Abono #{self.numero_abono} al Préstamo de {self.prestamo.empleado.nombre} por ${self.monto_cobrado}"

    def save(self, *args, **kwargs):
        # Solo hacer cálculos automáticos cuando el abono es nuevo.
        if not self.pk:
            # Tomar el saldo actual del préstamo antes de aplicar el nuevo abono.
            saldo_anterior = self.prestamo.saldo_actual
            
            # Calcular interés del periodo usando la tasa mensual del préstamo.
            self.monto_interes = saldo_anterior * (self.prestamo.tasa_interes_mensual / 100)
            
            # El capital pagado es el pago fijo definido en el préstamo.
            self.monto_capital = self.prestamo.pago_fijo_capital
            
            # El total cobrado es capital + interés.
            self.monto_cobrado = self.monto_capital + self.monto_interes
            
            # Actualizar el saldo restante después del pago.
            self.saldo_actual = saldo_anterior - self.monto_capital
            
            # Sincronizar el nuevo saldo en el préstamo.
            self.prestamo.saldo_actual = self.saldo_actual
            
            # Si el saldo llega a cero o menos, el préstamo termina.
            if self.saldo_actual <= 0:
                self.prestamo.estado = 'CONCLUIDO'
                
            # Calcular el número consecutivo del abono.
            ultimo_abono = Abono.objects.filter(prestamo=self.prestamo).order_by('-numero_abono').first()
            self.numero_abono = ultimo_abono.numero_abono + 1 if ultimo_abono else 1
            
            # Guardar primero el préstamo con su nuevo saldo.
            self.prestamo.save()
            
        # Guardar finalmente el abono.
        super().save(*args, **kwargs)