from django.urls import path

from . import views

urlpatterns = [
    path("", views.prestamo_list, name="prestamo_list"),
    path("nuevo/", views.prestamo_create, name="prestamo_create"),
    path("<int:pk>/", views.prestamo_detail, name="prestamo_detail"),
    path("<int:pk>/editar/", views.prestamo_update, name="prestamo_update"),
    path("<int:pk>/eliminar/", views.prestamo_delete, name="prestamo_delete"),

    # Acciones rápidas de estado
    path("<int:pk>/aprobar/", views.prestamo_aprobar, name="prestamo_aprobar"),
    path("<int:pk>/rechazar/", views.prestamo_rechazar, name="prestamo_rechazar"),
    path("<int:pk>/liberar/", views.prestamo_liberar, name="prestamo_liberar"),

    # Abonos
    path("<int:pk>/abonar/", views.abono_crear, name="abono_crear"),
    path("<int:pk>/abonos/", views.abono_list, name="abono_list"),
]
