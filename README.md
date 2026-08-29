# Level Works

Sistema de gestión y reserva, optimizado para negocios de autolavado. Desarrollado bajo una arquitectura de **monolito moderno** y asíncrono, eliminando la sobrecarga de frameworks frontend pesados para garantizar un rendimiento, menor complejidad de mantenimiento y un despliegue simplificado.

---

## Stack Tecnológico 

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
| **Pillow** | 10.0+ | Procesamiento de imágenes (requerido por fastapi-storages ImageType). |
| **Passlib & Bcrypt** | 1.7+ / 4.0+ | Hashing seguro de contraseñas y autenticación de administradores. |
| **Docker & Docker Compose** | v2+ | Contenedorización y orquestación del backend y la base de datos. |


---

## Estructura del Proyecto

```text
level-works/
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── create_admin.py
├── DockerCMD.md
├── db.md
├── README.md
│
└── app/
    ├── __init__.py
    ├── main.py                    # FastAPI(), lifespan, SQLAdmin, mount estáticos, routers
    ├── auth.py                    # AdminAuth (backend de login de SQLAdmin)
    ├── config.py                  # pydantic-settings, settings_proxy
    │
    ├── core/                      # Infraestructura transversal (no sabe nada del negocio)
    │   ├── __init__.py
    │   ├── security.py            # hash_password, verify_password (bcrypt/passlib)
    │   ├── storage.py             # FileSystemStorage, FileType/ImageType (fastapi-storages)
    │   └── db/
    │       ├── __init__.py
    │       └── database.py        # engine async, sessionmaker, get_db, init_db, Base
    │
    ├── models/                    # Tablas SQLAlchemy (antes era un solo models.py)
    │   ├── __init__.py            # exporta: User, Rol, Permission, Client, Service, Reservation, ReservationStatus
    │   ├── user.py                # User, Rol, Permission
    │   ├── client.py              # Client
    │   ├── service.py             # Service (usa FileType de core/storage)
    │   └── reservation.py         # Reservation, ReservationStatus
    │
    ├── schemas/                   # Contratos Pydantic de la API (hoy sueltos arriba de api.py)
    │   ├── __init__.py
    │   ├── user.py                # UserRegisterSchema, UserLoginSchema, UserUpdateSchema
    │   ├── client.py               # ClientSchema, ClientUpdateSchema
    │   └── service.py              # ServiceSchema
    │
    ├── services/                  # Lógica de negocio reutilizable (aislada de HTTP)
    │   ├── __init__.py
    │   ├── reservation_service.py # crear_reserva(), cancelar_reserva()
    │   ├── catalog_service.py     # listar_servicios(), CRUD
    │   └── user_service.py        # crear_usuario(), editar_usuario()
    │
    ├── routes/
    │   ├── __init__.py
    │   ├── views.py               # HTML/HTMX para el cliente final
    │   └── api.py                 # JSON para endpoints y panel admin
    │
    ├── img/                       # Fotos de servicios subidas vía SQLAdmin
    │   └── .gitkeep
    │
    └── templates/
        ├── base.html
        ├── home.html
        ├── servicios.html
        ├── reservas.html
        ├── components/
        │   └── horas_disponibles.html
        └── reservas/
            ├── step1_services.html
            ├── step2_datetime.html
            ├── horas_disponibles_reserva.html
            ├── step3_details.html
            └── step4_receipt.html
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
   cd level-works
   ```

2. **Configurar variables de entorno:**
   Crea tu archivo `.env` copiando el archivo de plantilla `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Contenido por defecto de `.env.example`:
   ```env
   DB_NAME=levelworks_db
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
   docker exec -it level-works-web-1 python create_admin.py
   ```
   Sigue las instrucciones en pantalla para ingresar Email, Username y Contraseña.

5. **Acceder a la aplicación:**
   * **Sitio Web / Reservas:** [http://localhost:8000](http://localhost:8000)
   * **Panel Administrativo:** [http://localhost:8000/admin](http://localhost:8000/admin)

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
