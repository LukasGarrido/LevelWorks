# Xperience

Sistema moderno de gestión y reserva de citas optimizado para negocios de autolavado. Desarrollado bajo una arquitectura de **monolito moderno** y asíncrono, eliminando la sobrecarga de frameworks frontend pesados para garantizar un rendimiento ultrarrápido, menor complejidad de mantenimiento y un despliegue simplificado.

---

## Factibilidad Técnica

| Tecnología | Versión | Breve Descripción |
| :--- | :--- | :--- |
| **FastAPI** | 0.110+ (Python 3.12) | Framework backend asíncrono de alto rendimiento para API y enrutamiento. |
| **HTMX** | 1.9+ | Frontend reactivo que realiza peticiones AJAX y actualiza HTML sin build step. |
| **Tailwind CSS** | 3.x (CDN) | Framework CSS utility-first para estilizado responsivo sin compilación local. |
| **Jinja2** | 3.1+ | Motor de plantillas para renderizado HTML en servidor (SSR). |
| **SQLAlchemy** | 2.0+ | ORM asíncrono para la gestión y modelado relacional de datos. |
| **PostgreSQL** | 16 | Base de datos relacional principal para entornos de producción. |
| **SQLAdmin** | 0.17+ | Panel de administración integrado para gestión CRUD de modelos y archivos. |
| **fastapi-storages** | 0.3+ | Almacenamiento y gestión nativa de archivos para SQLAlchemy y SQLAdmin. |
| **Passlib & Bcrypt** | 1.7+ / 4.0+ | Hashing seguro de contraseñas y autenticación de administradores. |
| **Docker & Docker Compose** | v2+ | Contenedorización y orquestación del backend y la base de datos. |


---

## Estructura del Proyecto

```text
xperience/
├── .env.example           # Plantilla con variables de entorno de ejemplo (DB credentials, contacto, etc.)
├── .gitignore             # Exclusiones de Git para Python, bytecode, DBs y Docker
├── Dockerfile             # Definición de la imagen Docker (Python 3.12-slim + uvicorn)
├── docker-compose.yml     # Orquestación del servicio PostgreSQL 16 + App FastAPI
├── requirements.txt       # Lista de dependencias de Python
├── create_admin.py        # Script de consola interactivo para crear usuarios administradores
├── DockerCMD.md            # Guía rápida de comandos Docker útiles para el proyecto
├── db.md                  # Referencia de comandos interactivos de PostgreSQL (psql)
├── README.md              # Documentación principal del proyecto
└── app/
    ├── __init__.py
    ├── auth.py            # Backend de autenticación de SQLAdmin (AdminAuth)
    ├── config.py          # Gestión centralizada de configuración (pydantic-settings)
    ├── database.py        # Motor asíncrono SQLAlchemy, sesión y creador de tablas (init_db)
    ├── main.py            # Entrada principal FastAPI, vista Admin (SQLAdmin) y estáticos
    ├── models.py          # Modelos relacionales (User, Client, Service, Reservation) y Enums
    ├── security.py        # Utilidades de seguridad (hashing y verificación Bcrypt)
    ├── storage.py         # Almacenamiento y gestión de archivos con FileSystemStorage
    ├── img/               # Almacenamiento de imágenes de servicios subidas por el admin
    ├── routes/
    │   ├── __init__.py
    │   ├── api.py         # Endpoints de API REST (CRUD admin, gestión de usuarios)
    │   └── views.py       # Rutas HTML y fragmentos HTMX del wizard de reservas
    └── templates/
        ├── base.html      # Plantilla base (Navbar, Modal de contacto, Footer, Tailwind, HTMX)
        ├── home.html      # Landing page principal (Hero, Beneficios, Grilla de Servicios)
        ├── servicios.html # Catálogo completo de servicios de detailing
        ├── reservas.html  # Contenedor del wizard multi-paso de reserva
        └── reservas/      # Fragmentos dinámicos HTMX del wizard
            ├── step1_services.html            # Paso 1: Selección de Servicio
            ├── step2_datetime.html            # Paso 2: Selección de Fecha y Calendario
            ├── horas_disponibles_reserva.html # Carga dinámica de horarios disponibles
            ├── step3_details.html             # Paso 3: Formulario de datos del cliente
            └── step4_receipt.html             # Paso 4: Recibo / Confirmación de éxito
```

---

## Cómo Levantarlo

### Prerrequisitos

* [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados (opción recomendada), **o**
* [Python 3.10+](https://www.python.org/) y [PostgreSQL](https://www.postgresql.org/) (para ejecución local nativa).

---

### Opción 1: Con Docker Compose (Recomendado)

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd xperience
   ```

2. **Configurar variables de entorno:**
   Crea tu archivo `.env` copiando el archivo de plantilla `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Contenido por defecto de `.env.example`:
   ```env
   DB_NAME=xperience_db
   DB_USER=postgres
   DB_PASSWORD=123
   ```

3. **Levantar los servicios:**
   ```bash
   docker-compose up -d --build
   ```
   Esto iniciará el contenedor de PostgreSQL 16 y la aplicación FastAPI en Uvicorn.

4. **Crear el usuario Administrador:**
   Ejecuta el script interactivo dentro del contenedor de la app:
   ```bash
   docker exec -it xperience-web-1 python create_admin.py
   ```
   Sigue las instrucciones en pantalla para ingresar Email, Username y Contraseña.

5. **Acceder a la aplicación:**
   * **Sitio Web / Reservas:** [http://localhost:8000](http://localhost:8000)
   * **Panel Administrativo:** [http://localhost:8000/admin](http://localhost:8000/admin)

---

### Opción 2: Ejecución Local Nativa (Sin Docker)

1. **Crear y activar un entorno virtual:**
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar el entorno (`.env`):**
   Copia el archivo `.env.example` a `.env`. Si no especificas variables de PostgreSQL en el `.env`, la aplicación utilizará SQLite por defecto (`sqlite+aiosqlite:///./xperience.db`).

4. **Crear usuario Administrador:**
   ```bash
   python create_admin.py
   ```

5. **Iniciar el servidor Uvicorn:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## Cómo se Usa

### 1. Reservar una Cita (Experiencia del Cliente)

1. Ingresa a `http://localhost:8000`.
2. **Selecciona un Servicio:** Elige entre los servicios de autolavado disponibles (ej: Lavado Simple, Lavado Completo, Polimerizado).
3. **Selecciona una Fecha:** Al elegir un día en el calendario, HTMX envía automáticamente una solicitud asíncrona para consultar las horas disponibles.
4. **Elige un Horario:** Selecciona uno de los bloques de hora disponibles devueltos dinámicamente.
5. **Completa los Datos:** Ingresa Nombre, Correo Electrónico, Teléfono y Notas adicionales.
6. **Confirmar Reserva:** Al enviar el formulario, el cliente recibe una confirmación instantánea sin recarga de página.

### 2. Gestión Administrativa (Panel Admin)

1. Accede a `http://localhost:8000/admin`.
2. Inicia sesión con tus credenciales de administrador creadas con `create_admin.py`.
3. **Módulos Disponibles:**
   * **Servicios:** Crea, edita o elimina servicios. Puedes subir imágenes asociadas que se almacenarán en `/app/img/`.
   * **Clientes:** Visualiza el listado de clientes registrados automáticamente al reservar.
   * **Reservas:** Revisa todas las citas agendadas, filtra por estado y actualiza su estatus (*pendiente*, *confirmada*, *en_progreso*, *completada*, *cancelada*).
   * **Usuarios:** Gestiona usuarios internos del sistema, asignando roles y permisos específicos.

---

## Comandos Útiles

Consulta los archivos complementarios para comandos específicos:
* [DockerCMD.md](file:///c:/Users/lukas/Desktop/Personal/xperience/DockerCMD.md) - Comandos rápidos para manejar contenedores Docker.
* [db.md](file:///c:/Users/lukas/Desktop/Personal/xperience/db.md) - Comandos útiles para consultas en la CLI de PostgreSQL (`psql`).
