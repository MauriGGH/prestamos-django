# Sesión 1: Fundamentos de Docker y Django

**Duración estimada:** 3-4 horas  
**Nivel:** Principiante

## 🎯 Objetivos de la Sesión

Al finalizar esta sesión, podrás:

- ✅ Entender qué es Docker y para qué sirve
- ✅ Comprender los conceptos básicos de Django
- ✅ Configurar tu entorno de desarrollo con Docker
- ✅ Crear tu primer proyecto Django
- ✅ Crear los modelos básicos del sistema de préstamos

---

## 📚 Parte 1: Introducción a Docker

### ¿Qué es Docker?

Docker es una herramienta que te permite **empaquetar aplicaciones** junto con todo lo que necesitan para funcionar (librerías, dependencias, configuraciones) en "contenedores".

**Analogía simple:**

- Imagina que tu aplicación es como una planta.
- Normalmente necesitarías tierra específica, temperatura adecuada, etc.
- Docker es como una maceta portátil que incluye todo lo necesario.
- Puedes mover la maceta a cualquier lugar y la planta funcionará igual.

### ¿Por qué usar Docker?

✅ **Funciona en todos lados:** "En mi máquina funciona" → con Docker funciona en todas las máquinas  
✅ **Fácil instalación:** No necesitas instalar Python, PostgreSQL, etc. manualmente  
✅ **Aislamiento:** Tu proyecto no afecta otros proyectos  
✅ **Reproducible:** Todos en el equipo tienen el mismo entorno

### Conceptos Clave

#### 1. Imagen (Image)

Es como una "receta" o "plantilla" que define:

- Sistema operativo base
- Software instalado
- Configuración inicial

```
Ejemplo: imagen de Python 3.11 con Django ya instalado
```

#### 2. Contenedor (Container)

Es una "instancia en ejecución" de una imagen.

```
Analogía: La imagen es el plano de una casa, el contenedor es la casa construida
```

#### 3. Dockerfile

Archivo de texto que contiene las instrucciones para crear una imagen.

```dockerfile
# Ejemplo básico
FROM python:3.11          # Usa Python 3.11 como base
WORKDIR /app              # Crea carpeta de trabajo
COPY . /app               # Copia archivos
RUN pip install django    # Instala Django
```

#### 4. Docker Compose

Herramienta para definir y ejecutar aplicaciones con **múltiples contenedores**.

```
En nuestro proyecto:
- 1 contenedor para Django (nuestra aplicación)
- 1 contenedor para PostgreSQL (base de datos)
```

### Verificación de Docker

Abre tu terminal y ejecuta:

```bash
# Verificar versión de Docker
docker --version

# Verificar Docker Compose
docker compose version

# Probar que Docker funciona
docker run hello-world
```

✅ **Checkpoint:** Si ves mensajes de éxito, Docker está listo.

---

## 📚 Parte 2: Introducción a Django

### ¿Qué es Django?

Django es un **framework web** de Python que te ayuda a crear sitios web y aplicaciones web de forma rápida y estructurada.

**Analogía simple:**

- Sin framework: Construir una casa desde cero (hacer ladrillos, cimientos, todo)
- Con Django: Tienes las paredes, techo, puertas ya hechas, solo las organizas y personalizas

### ¿Por qué Django?

✅ **Completo:** Incluye todo lo necesario (base de datos, autenticación, Admin)  
✅ **Seguro:** Protege contra errores comunes de seguridad  
✅ **Rápido de desarrollar:** Menos código, más funcionalidad  
✅ **Bien documentado:** Excelente documentación oficial

### Arquitectura MTV (Model-Template-View)

Django usa el patrón **MTV**, similar a MVC:

```
┌─────────────────────────────────────┐
│  USUARIO hace una petición         │
└──────────────┬──────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  URLs (urls.py)                      │
│  "¿Qué dirección pidió el usuario?"  │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  VISTA (views.py)                    │
│  "¿Qué lógica ejecutar?"             │
│  - Obtiene datos del Modelo          │
│  - Procesa información               │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  MODELO (models.py)                  │
│  "¿Qué datos necesitas?"             │
│  - Interactúa con la base de datos   │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  TEMPLATE (archivo.html)             │
│  "¿Cómo mostrar los datos?"          │
│  - Renderiza la página HTML          │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  RESPUESTA al usuario                │
└──────────────────────────────────────┘
```

### Componentes Principales

#### 1. Modelos (Models)

Definen la estructura de tus datos (tablas de la base de datos).

```python
# Ejemplo simple
class Empleado(models.Model):
    nombre = models.CharField(max_length=200)
    fecha_ingreso = models.DateField()
```

#### 2. Vistas (Views)

Contienen la lógica de negocio.

```python
# Ejemplo simple
def listar_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'empleados.html', {'empleados': empleados})
```

#### 3. Templates

Archivos HTML que muestran información al usuario.

```html
<!-- Ejemplo simple -->
<h1>Lista de Empleados</h1>
{% for empleado in empleados %}
<p>{{ empleado.nombre }}</p>
{% endfor %}
```

#### 4. URLs

Mapean direcciones web a vistas.

```python
# Ejemplo simple
urlpatterns = [
    path('empleados/', listar_empleados),
]
```

---

## 🛠️ Parte 3: Configuración del Proyecto

### Paso 1: Crear la Estructura del Proyecto

```bash
# 1. Crear carpeta del proyecto
mkdir sistema_prestamos
cd sistema_prestamos

# 2. Crear archivo para dependencias
# Crea requirements.txt con el siguiente contenido:
```

**Archivo: `requirements.txt`**

```txt
Django==5.0.2
psycopg2-binary==2.9.9
python-decouple==3.8
```

### Paso 2: Crear el Dockerfile

**Archivo: `Dockerfile`**

```dockerfile
# Imagen base de Python
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de requisitos
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Puerto de Django
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Paso 3: Crear docker-compose.yml

**Archivo: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  # Base de datos PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: prestamos_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=prestamos_db
      - POSTGRES_USER=prestamos_user
      - POSTGRES_PASSWORD=prestamos_password
    ports:
      - '5432:5432'

  # Aplicación Django
  web:
    build: .
    container_name: prestamos_web
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - '8000:8000'
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://prestamos_user:prestamos_password@db:5432/prestamos_db
    depends_on:
      - db

volumes:
  postgres_data:
```

### Paso 4: Iniciar Docker y Crear Proyecto Django

```bash
# 1. Construir las imágenes
docker compose build

# 2. Crear proyecto Django (solo la primera vez)
docker compose run web django-admin startproject config .

# 3. Verificar que se creó manage.py
ls
# Debes ver: manage.py, config/, requirements.txt, etc.
```

### Paso 5: Configurar la Base de Datos

Edita el archivo `config/settings.py` y busca la sección `DATABASES`:

```python
# config/settings.py

# Antes (SQLite):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Después (PostgreSQL):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'prestamos_db',
        'USER': 'prestamos_user',
        'PASSWORD': 'prestamos_password',
        'HOST': 'db',
        'PORT': '5432',
    }
}
```

También actualiza la configuración de idioma y zona horaria:

```python
# config/settings.py

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
```

### Paso 6: Levantar el Proyecto

```bash
# Iniciar los servicios
docker compose up

# Deberías ver algo como:
# web_1  | Starting development server at http://0.0.0.0:8000/
```

Abre tu navegador y ve a: **http://localhost:8000**

✅ **Checkpoint:** Deberías ver la página de bienvenida de Django.

---

## 🏗️ Parte 4: Crear los Modelos

### Paso 1: Crear la App de Empleados

```bash
# Detén el servidor (Ctrl+C) o abre otra terminal

# Crear la app
docker compose exec web python manage.py startapp empleados
```

Esto crea la estructura:

```
empleados/
├── __init__.py
├── admin.py
├── apps.py
├── models.py      ← Aquí definiremos nuestros modelos
├── tests.py
└── views.py
```

### Paso 2: Registrar la App

Edita `config/settings.py`:

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'empleados',  # ← Agregar esta línea
]
```

### Paso 3: Definir el Modelo Puesto

Abre `empleados/models.py` y escribe:

```python
# empleados/models.py
from django.db import models

class Puesto(models.Model):
    """
    Catálogo de puestos de trabajo en la empresa.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre del puesto de trabajo"
    )
    sueldo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Sueldo mensual en pesos"
    )

    class Meta:
        verbose_name = "Puesto"
        verbose_name_plural = "Puestos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
```

**Explicación:**

- `CharField`: Campo de texto con longitud máxima
- `DecimalField`: Campo numérico con decimales (ideal para dinero)
- `unique=True`: No permite valores duplicados
- `help_text`: Texto de ayuda
- `class Meta`: Configuración adicional
- `__str__`: Cómo se muestra el objeto como texto

### Paso 4: Definir el Modelo Empleado

Continúa en el mismo archivo:

```python
# empleados/models.py (continuar)

class Empleado(models.Model):
    """
    Información de empleados de la empresa.
    """
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre completo del empleado"
    )
    fecha_ingreso = models.DateField(
        help_text="Fecha de ingreso a la empresa"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el empleado está activo"
    )

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
```

### Paso 5: Definir el Modelo HistorialPuesto

```python
# empleados/models.py (continuar)

class HistorialPuesto(models.Model):
    """
    Registro histórico de puestos por empleado.
    """
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='historial_puestos',
        help_text="Empleado al que pertenece el historial"
    )
    puesto = models.ForeignKey(
        Puesto,
        on_delete=models.PROTECT,
        help_text="Puesto asignado"
    )
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio en el puesto"
    )
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de finalización (NULL si es puesto actual)"
    )

    class Meta:
        verbose_name = "Historial de Puesto"
        verbose_name_plural = "Historiales de Puestos"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado.nombre} - {self.puesto.nombre}"
```

**Explicación de ForeignKey:**

- `ForeignKey`: Relación "muchos a uno"
- `on_delete=models.CASCADE`: Si se elimina el empleado, elimina sus historiales
- `on_delete=models.PROTECT`: No permite eliminar un puesto si está en uso
- `related_name`: Nombre para acceder desde el otro lado de la relación

### Paso 6: Crear las Migraciones

Las migraciones son como "versiones" de tu base de datos:

```bash
# Crear las migraciones
docker compose exec web python manage.py makemigrations

# Deberías ver algo como:
# Migrations for 'empleados':
#   empleados/migrations/0001_initial.py
#     - Create model Puesto
#     - Create model Empleado
#     - Create model HistorialPuesto
```

### Paso 7: Aplicar las Migraciones

```bash
# Aplicar las migraciones a la base de datos
docker compose exec web python manage.py migrate

# Deberías ver:
# Running migrations:
#   Applying empleados.0001_initial... OK
```

✅ **Checkpoint:** Las tablas fueron creadas en PostgreSQL.

### Paso 8: Verificar en PostgreSQL

```bash
# Conectarse a PostgreSQL
docker compose exec db psql -U prestamos_user -d prestamos_db

# Listar tablas
\dt

# Deberías ver:
# empleados_puesto
# empleados_empleado
# empleados_historialpuesto

# Salir
\q
```

---

## 🎨 Parte 5: Django Admin

Django incluye una interfaz de administración automática.

### Paso 1: Registrar los Modelos en el Admin

Edita `empleados/admin.py`:

```python
# empleados/admin.py
from django.contrib import admin
from .models import Puesto, Empleado, HistorialPuesto

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'sueldo']
    search_fields = ['nombre']

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_ingreso', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
    date_hierarchy = 'fecha_ingreso'

@admin.register(HistorialPuesto)
class HistorialPuestoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'puesto', 'fecha_inicio', 'fecha_fin']
    list_filter = ['puesto']
    search_fields = ['empleado__nombre']
```

### Paso 2: Crear un Superusuario

```bash
docker compose exec web python manage.py createsuperuser

# Sigue las instrucciones:
# Username: admin
# Email: admin@example.com
# Password: admin123
# Password (again): admin123
```

### Paso 3: Acceder al Admin

1. Ve a: **http://localhost:8000/admin**
2. Inicia sesión con tu usuario y contraseña
3. Verás la interfaz de administración

✅ **Checkpoint:** Puedes ver "Empleados", "Puestos" e "Historiales de Puestos".

### Paso 4: Crear Datos de Prueba

1. Haz clic en "Puestos" → "Agregar Puesto"
2. Crea algunos puestos:
   - PROGRAMADOR JR - 16000
   - PROGRAMADOR SENIOR - 40000
   - ARQUITECTO DE SOFTWARE - 50000

3. Haz clic en "Empleados" → "Agregar Empleado"
4. Crea algunos empleados con fechas de ingreso

5. Haz clic en "Historiales de Puestos" → "Agregar"
6. Asigna puestos a los empleados

---

## 📝 Ejercicio Práctico

**Reto:** Crea un modelo simple llamado `Prestamo` con los campos básicos.

```python
# empleados/models.py (agregar al final)

class Prestamo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_solicitud = models.DateField()

    def __str__(self):
        return f"Préstamo #{self.id} - {self.empleado.nombre}"
```

Pasos:

1. Agregar el modelo
2. Hacer migraciones: `docker compose exec web python manage.py makemigrations`
3. Aplicar migraciones: `docker compose exec web python manage.py migrate`
4. Registrar en admin.py
5. Crear un préstamo desde el admin

---

## 📚 Resumen de Comandos Importantes

```bash
# Iniciar servicios
docker compose up

# Detener servicios
docker compose down

# Ver logs
docker compose logs -f web

# Crear migraciones
docker compose exec web python manage.py makemigrations

# Aplicar migraciones
docker compose exec web python manage.py migrate

# Crear superusuario
docker compose exec web python manage.py createsuperuser

# Shell de Django (para probar código)
docker compose exec web python manage.py shell

# Conectar a PostgreSQL
docker compose exec db psql -U prestamos_user -d prestamos_db
```

---

## ✅ Checklist de la Sesión

- [ ] Docker instalado y funcionando
- [ ] Docker Compose configurado
- [ ] Proyecto Django creado
- [ ] Base de datos PostgreSQL conectada
- [ ] Modelos creados (Puesto, Empleado, HistorialPuesto)
- [ ] Migraciones aplicadas
- [ ] Django Admin accesible
- [ ] Datos de prueba creados

---

## 🎯 Para la Próxima Sesión

Prepárate para:

- Agregar validaciones a los modelos
- Crear el modelo completo de Préstamos y Abonos
- Implementar métodos personalizados
- Crear una API básica

---

## 📖 Recursos Adicionales

- [Documentación oficial de Django](https://docs.djangoproject.com/)
- [Tutorial de Django](https://docs.djangoproject.com/en/5.0/intro/tutorial01/)
- [Documentación de Docker](https://docs.docker.com/)

---

**¡Felicidades!** Has completado la primera sesión. Ya tienes las bases para construir el sistema de préstamos. 🎉
