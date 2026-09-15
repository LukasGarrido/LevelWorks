# Level Works

Sistema de gestión y reserva, optimizado para negocios de autolavado. Desarrollado bajo una **arquitectura desacoplada**: un backend API-first construido con FastAPI y un frontend independiente construido con Astro, comunicados vía REST/JSON.

---

## Stack Tecnológico

### Backend (API)

| Tecnología | Versión | Breve Descripción |
| :--- | :--- | :--- |
| **FastAPI** | 0.110+ (Python 3.12) | Framework backend asíncrono de alto rendimiento, expuesto como API JSON pura bajo `/api/v1`. |
| **SQLAlchemy** | 2.0+ | ORM asíncrono para la gestión y modelado relacional de datos. |
| **PostgreSQL** | 16 | Base de datos relacional principal para entornos de producción. |
| **Pydantic** | 2.x | Contratos de entrada/salida tipados (schemas) para cada endpoint. |
| **python-jose / PyJWT** | — | Emisión y validación de tokens JWT para autenticación de la API. |
| **SQLAdmin** | 0.17+ | Panel de administración integrado (SSR interno, no forma parte del frontend público). |
| **fastapi-storages** | 0.3+ | Almacenamiento y gestión nativa de archivos para SQLAlchemy y SQLAdmin. |
| **Pillow** | 10.0+ | Procesamiento de imágenes (requerido por fastapi-storages ImageType). |
| **Passlib & Bcrypt** | 1.7+ / 4.0+ | Hashing seguro de contraseñas. |

### Frontend

| Tecnología | Versión | Breve Descripción |
| :--- | :--- | :--- |
| **Astro** | 4.x | Framework frontend, renderizado estático/SSR con islas de interactividad. |
| **React / TS** | — | Componentes interactivos (islands) para el flujo de reserva: selección de servicio, fecha, horario. |
| **Tailwind CSS** | 3.x | Framework CSS utility-first para estilizado responsivo. |

### Infraestructura

| Tecnología | Versión | Breve Descripción |
| :--- | :--- | :--- |
| **Docker & Docker Compose** | v2+ | Contenedorización y orquestación de backend, frontend y base de datos como servicios independientes. |

---

## Estructura del Proyecto

```text
level-works/
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── db.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── create_admin.py
│   ├── DockerCMD.md
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py                     # FastAPI(), lifespan, CORS, SQLAdmin, incluye api/v1
│       ├── auth.py                     # AdminAuth (backend de login de SQLAdmin)
│       ├── config.py                   # pydantic-settings, settings_proxy, CORS_ORIGINS
│       │
│       ├── core/                       # Infraestructura transversal (no sabe nada del negocio)
│       │   ├── __init__.py
│       │   ├── security.py             # hash_password, verify_password
│       │   ├── jwt.py                  # create_access_token, decode_token
│       │   ├── storage.py              # FileSystemStorage, FileType/ImageType
│       │   └── db/
│       │       ├── __init__.py
│       │       └── database.py         # engine async, sessionmaker, get_db, init_db, Base
│       │
│       ├── models/                     # Tablas SQLAlchemy
│       │   ├── __init__.py             # exporta: User, Rol, Permission, Client, Service, Reservation, ReservationStatus
│       │   ├── user.py
│       │   ├── client.py
│       │   ├── service.py
│       │   └── reservation.py
│       │
│       ├── schemas/                    # Contratos Pydantic de la API
│       │   ├── __init__.py
│       │   ├── auth.py                 # TokenSchema, LoginSchema
│       │   ├── user.py                 # UserRegisterSchema, UserLoginSchema, UserUpdateSchema, UserResponseSchema
│       │   ├── client.py                # ClientSchema, ClientUpdateSchema
│       │   ├── service.py               # ServiceSchema, ServiceResponseSchema
│       │   └── reservation.py           # ReservationCreateSchema, ReservationResponseSchema, AvailableSlotsSchema
│       │
│       ├── services/                   # Lógica de negocio reutilizable (aislada de HTTP)
│       │   ├── __init__.py
│       │   ├── auth_service.py         # login(), issue_token()
│       │   ├── reservation_service.py  # crear_reserva(), cancelar_reserva(), horas_disponibles()
│       │   ├── catalog_service.py      # listar_servicios(), CRUD
│       │   └── user_service.py         # crear_usuario(), editar_usuario()
│       │
│       ├── api/                        # Endpoints HTTP, organizados por dominio
│       │   ├── __init__.py
│       │   ├── deps.py                 # get_current_user, require_role, paginación común
│       │   └── v1/
│       │       ├── __init__.py         # router principal, prefix="/api/v1"
│       │       ├── auth.py             # POST /login, POST /refresh
│       │       ├── users.py            # CRUD usuarios/roles/permisos
│       │       ├── clients.py          # CRUD clientes
│       │       ├── services.py         # GET /services, catálogo público
│       │       └── reservations.py     # POST /reservations, GET /availability, PATCH /:id/status
│       │
│       └── img/                        # Fotos de servicios subidas vía SQLAdmin
│           └── .gitkeep
│
└── frontend/
    ├── Dockerfile
    ├── astro.config.mjs
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.mjs
    │
    ├── public/
    │   └── favicon.svg
    │
    └── src/
        ├── env.d.ts
        │
        ├── lib/
        │   ├── api.ts               # cliente fetch tipado (PUBLIC_API_URL)
        │   └── types.ts             # tipos compartidos: Service, Reservation, Slot...
        │
        ├── layouts/
        │   └── Base.astro
        │
        ├── components/
        │   ├── Navbar.astro
        │   ├── Footer.astro
        │   ├── ServiceCard.astro
        │   └── reservation/
        │       ├── ServiceSelect.tsx      # island
        │       ├── DatePicker.tsx         # island
        │       ├── TimeSlots.tsx          # island
        │       └── ReservationForm.tsx    # island
        │
        └── pages/
            ├── index.astro
            ├── servicios.astro
            └── reservas.astro
```

> **Qué cambió respecto a la versión anterior:** `app/routes/views.py` y `app/templates/` (Jinja2 + HTMX) fueron eliminados por completo. El renderizado de cliente ahora vive enteramente en `frontend/`, y el backend expone únicamente JSON bajo `/api/v1`. SQLAdmin se mantiene como panel administrativo interno (sigue siendo SSR, pero no forma parte del frontend público).

---

## Cómo Levantarlo

### Prerrequisitos

* [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados (opción recomendada), **o**
* [Python 3.10+](https://www.python.org/), [Node.js 20+](https://nodejs.org/) y [PostgreSQL](https://www.postgresql.org/) (para ejecución local nativa).

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
   # Base de datos
   DB_NAME=levelworks_db
   DB_USER=postgres
   DB_PASSWORD=123

   # Backend
   JWT_SECRET=changeme
   CORS_ORIGINS=http://localhost:4321

   # Frontend
   PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

3. **Levantar los servicios:**
   ```bash
   docker-compose up -d --build
   ```
   Esto iniciará tres contenedores: `db` (PostgreSQL 16), `api` (FastAPI en Uvicorn) y `frontend` (Astro).

4. **Crear el usuario Administrador:**
   Ejecuta el script interactivo dentro del contenedor de la API:
   ```bash
   docker exec -it level-works-api-1 python create_admin.py
   ```
   Sigue las instrucciones en pantalla para ingresar Email, Username y Contraseña.

5. **Acceder a la aplicación:**
   * **Sitio Web / Reservas (Astro):** [http://localhost:4321](http://localhost:4321)
   * **API (FastAPI):** [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
   * **Documentación interactiva (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Panel Administrativo:** [http://localhost:8000/admin](http://localhost:8000/admin)

---

## Cómo se Usa

### 1. Reservar una Cita (Experiencia del Cliente)

1. Ingresa a `http://localhost:4321`.
2. **Selecciona un Servicio:** Elige entre los servicios de autolavado disponibles (ej: Lavado Simple, Lavado Completo, Polimerizado), obtenidos desde `GET /api/v1/services`.
3. **Selecciona una Fecha:** Al elegir un día en el calendario, el componente `TimeSlots` consulta `GET /api/v1/availability` de forma asíncrona.
4. **Elige un Horario:** Selecciona uno de los bloques de hora disponibles devueltos por la API.
5. **Completa los Datos:** Ingresa Nombre, Correo Electrónico, Teléfono y Notas adicionales.
6. **Confirmar Reserva:** El formulario envía `POST /api/v1/reservations` y muestra la confirmación sin recarga de página.

### 2. Gestión Administrativa (Panel Admin)

1. Accede a `http://localhost:8000/admin`.
2. Inicia sesión con tus credenciales de administrador creadas con `create_admin.py`.
3. **Módulos Disponibles:**
   * **Servicios:** Crea, edita o elimina servicios. Puedes subir imágenes asociadas que se almacenarán en `/app/img/`.
   * **Clientes:** Visualiza el listado de clientes registrados automáticamente al reservar.
   * **Reservas:** Revisa todas las citas agendadas, filtra por estado y actualiza su estatus (*pendiente*, *confirmada*, *en_progreso*, *completada*, *cancelada*).
   * **Usuarios:** Gestiona usuarios internos del sistema, asignando roles y permisos específicos.

---

## API (`/api/v1`)

| Recurso | Endpoints principales |
| :--- | :--- |
| **Auth** | `POST /auth/login`, `POST /auth/refresh` |
| **Services** | `GET /services`, `GET /services/{id}` |
| **Reservations** | `POST /reservations`, `GET /availability`, `PATCH /reservations/{id}/status` |
| **Clients** | `GET /clients`, `GET /clients/{id}` |
| **Users** | `GET /users`, `POST /users`, `PATCH /users/{id}` |

Documentación completa e interactiva disponible en `/docs` (Swagger UI) y `/redoc`.

---

## Comandos de Base de Datos (PostgreSQL)

| Comando | Descripción | Ejemplo de uso |
| :--- | :--- | :--- |
| `\dt` | Lista todas las **tablas** disponibles en la base de datos actual. | `\dt` |
| `\d <tabla>` | Muestra la **estructura detallada** de una tabla (columnas, tipos de datos, llaves primarias, índices). | `\d services` |
| `\l` | Lista todas las **bases de datos** creadas en el servidor de Postgres. | `\l` |
| `\du` | Lista todos los **usuarios / roles** creados y sus respectivos permisos. | `\du` |
| `\df` | Lista todas las **funciones** o procedimientos almacenados. | `\df` |
| `\dn` | Lista los **esquemas** de la base de datos (por defecto verás `public`). | `\dn` |