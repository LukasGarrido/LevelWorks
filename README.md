# Level Works

Sistema de gestión y reserva, optimizado para negocios de autolavado. Desarrollado bajo una **arquitectura desacoplada**: un backend API-first construido con FastAPI y un frontend independiente construido con Astro (sin frameworks de UI), comunicados vía REST/JSON.

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
| **Astro** | 7.x | Framework frontend, build estático puro (`output: 'static'`). Sin framework de UI ni islands — interactividad con `<script>` module nativo. |
| **Tailwind CSS** | 4.x | Framework CSS utility-first, integrado vía `@tailwindcss/vite` (sin el integration clásico de v3). |
| **tw-animate-css** | 1.x | Utilidades de animación compatibles con Tailwind v4. |
| **TypeScript** | strict | Tipado del cliente API (`lib/api.ts`, `lib/types.ts`) y configuración del proyecto. |

### Infraestructura

| Tecnología | Versión | Breve Descripción |
| :--- | :--- | :--- |
| **Docker & Docker Compose** | v2+ | Contenedorización y orquestación de backend, frontend y base de datos como servicios independientes. Sin necesidad de instalar Node ni Python en la máquina local. |
| **nginx** | alpine | Sirve el build estático de Astro en producción. |

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
│   ├── docker/
│   │   └── Dockerfile
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
│       ├── core/
│       │   ├── security.py             # hash_password, verify_password
│       │   ├── jwt.py                  # create_access_token, decode_token
│       │   ├── storage.py              # FileSystemStorage, FileType/ImageType
│       │   └── db/
│       │       └── database.py         # engine async, sessionmaker, get_db, init_db, Base
│       │
│       ├── models/                     # Tablas SQLAlchemy
│       │   ├── user.py
│       │   ├── client.py
│       │   ├── service.py
│       │   └── reservation.py
│       │
│       ├── schemas/                    # Contratos Pydantic de la API
│       │   ├── auth.py
│       │   ├── user.py
│       │   ├── client.py
│       │   ├── service.py
│       │   └── reservation.py
│       │
│       ├── services/                   # Lógica de negocio reutilizable (aislada de HTTP)
│       │   ├── auth_service.py
│       │   ├── reservation_service.py
│       │   ├── catalog_service.py
│       │   └── user_service.py
│       │
│       ├── api/                        # Endpoints HTTP, organizados por dominio
│       │   ├── deps.py                 # get_current_user, require_role, paginación común
│       │   └── v1/
│       │       ├── __init__.py         # router principal, prefix="/api/v1"
│       │       ├── auth.py
│       │       ├── users.py
│       │       ├── clients.py
│       │       ├── services.py
│       │       └── reservations.py
│       │
│       └── img/                        # Fotos de servicios subidas vía SQLAdmin
│
└── frontend/
    ├── docker/
    │   ├── Dockerfile                  # Multi-stage: build estático + nginx (producción)
    │   └── Dockerfile.dev              # Node + astro dev con hot-reload (desarrollo)
    ├── astro.config.mjs
    ├── package.json
    ├── package-lock.json
    ├── tsconfig.json
    ├── .vscode/
    │
    ├── public/
    │   └── favicon.svg
    │
    └── src/
        ├── env.d.ts
        ├── styles/
        │   └── global.css              # entrada de Tailwind v4 (@import "tailwindcss")
        │
        ├── lib/
        │   ├── api.ts                  # cliente fetch tipado hacia FastAPI
        │   └── types.ts                # Service, Slot, ReservationPayload, ReservationResponse
        │
        ├── layouts/
        │   └── Base.astro
        │
        ├── components/
        │   ├── Navbar.astro
        │   ├── Footer.astro
        │   ├── ServiceCard.astro
        │   └── reservation/             # Wizard de reserva, orquestado con CustomEvents
        │       ├── ServiceSelect.astro
        │       ├── DatePicker.astro
        │       ├── TimeSlots.astro
        │       └── ReservationForm.astro
        │
        └── pages/
            ├── index.astro
            ├── servicios.astro
            └── reservas.astro
```

> **Qué cambió respecto a la versión anterior:** `app/routes/views.py` y `app/templates/` (Jinja2 + HTMX) fueron eliminados. El frontend ahora es un proyecto Astro independiente, **sin React ni ningún framework de UI** — toda la interactividad del flujo de reserva se resuelve con `<script>` nativo dentro de cada componente `.astro`, comunicándose entre sí vía `CustomEvent` en el `document`. El backend expone únicamente JSON bajo `/api/v1`. SQLAdmin se mantiene como panel administrativo interno (SSR, pero fuera del frontend público).

---

## Arquitectura del Frontend (Astro)

Sin framework de UI, el estado del wizard de reserva se comparte entre componentes mediante eventos del DOM, no props ni stores:

```
ServiceSelect ──(service:selected)──▶ DatePicker ──(date:selected)──▶ TimeSlots ──(slot:selected)──▶ ReservationForm
```

Cada componente escucha el evento del paso anterior, hace su propio fetch a la API vía `lib/api.ts`, y dispara su propio evento al completarse. Esto evita acoplar componentes entre sí y mantiene cada `.astro` autocontenido (markup + estilos + su propio script).

`output: 'static'` en `astro.config.mjs` — todo se compila a HTML/CSS/JS estático en build time; no hay SSR en producción, el servidor (nginx) solo sirve archivos.

---

## Cómo Levantarlo

### Prerrequisitos

* [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados. **No se necesita Node.js ni Python instalados localmente** — todo corre dentro de contenedores.

---

### Configurar variables de entorno

```bash
cp .env.example .env
```

```env
# Aplicación
APP_NAME=Level Works
DEBUG=True
SECRET_KEY=password

# Backend (API)
PORT=8000
CORS_ORIGINS=http://localhost:4323

# Frontend (Astro)
FRONTEND_PORT=4323
PUBLIC_API_URL=http://localhost:8000/api/v1

# Base de Datos
DB_NAME=levelworks_db
DB_USER=postgres
DB_PASSWORD=123
DB_PORT=5432

# Información de Contacto (Modal / Base HTML)
CONTACT_EMAIL=contacto@gmail
CONTACT_PHONE=+56912345678
INSTAGRAM_HANDLE=@xxxxxxxx
```

---

### Levantar todo el stack (producción)

```bash
docker-compose up -d --build
```

Levanta tres contenedores:
* `db` — PostgreSQL 16
* `api` — FastAPI en Uvicorn (`http://localhost:8000`)
* `frontend` — Astro compilado a estático, servido por nginx (`http://localhost:4323`)

**Crear el usuario Administrador:**
```bash
docker exec -it levelworks-api-1 python create_admin.py
```

**Acceder:**
* **Sitio Web / Reservas (Astro):** [http://localhost:4323](http://localhost:4323)
* **API (FastAPI):** [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
* **Docs interactivas (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Panel Administrativo:** [http://localhost:8000/admin](http://localhost:8000/admin)

> El servicio `frontend` usa build multi-stage: compila con Node y descarta todo el entorno de Node en la imagen final, quedándose solo con los archivos estáticos servidos por nginx. Por eso **cualquier cambio en `frontend/src/` requiere rebuild** (`docker-compose up --build frontend`) — no hay hot-reload en este modo.

---

### Desarrollo del frontend con hot-reload

Para iterar sobre componentes de Astro sin rebuildear en cada cambio, existe un servicio separado (`frontend-dev`) que corre `astro dev` con el código montado como volumen:

```bash
docker-compose up --build frontend-dev
```

Esto expone Astro en modo desarrollo en `http://localhost:4323` con recarga automática al guardar cualquier archivo en `src/`. No reemplaza al servicio `frontend` (producción) — se usan por separado, según lo que estés haciendo.

---

## Cómo se Usa

### 1. Reservar una Cita (Experiencia del Cliente)

1. Ingresa a `http://localhost:4323`.
2. **Selecciona un Servicio:** `ServiceSelect` obtiene el catálogo desde `GET /api/v1/services`.
3. **Selecciona una Fecha:** `DatePicker` se habilita tras elegir servicio; al elegir fecha dispara `date:selected`.
4. **Elige un Horario:** `TimeSlots` consulta `GET /api/v1/availability` y muestra los bloques disponibles.
5. **Completa los Datos:** `ReservationForm` se habilita tras elegir horario — Nombre, Correo, Teléfono, Notas.
6. **Confirmar Reserva:** Envía `POST /api/v1/reservations` y muestra la confirmación sin recarga de página.

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

---

## Comandos usados para levantar Astro (setup inicial, sin instalar Node localmente)

Estos dos comandos se corren **una sola vez**, desde la raíz del repo, para generar el scaffold del proyecto Astro y agregar Tailwind v4 — todo dentro de un contenedor efímero de Node, sin dejar nada instalado en la máquina local:

```bash
docker run --rm -it -v "${PWD}/frontend:/app" -w /app node:22-alpine sh -c "npm create astro@latest ."
```

```bash
docker run --rm -it -v "${PWD}/frontend:/app" -w /app node:22-alpine sh -c "npm install tailwindcss @tailwindcss/vite tw-animate-css"
```

> **Importante:** ambos comandos deben correrse parado en la **raíz del repo** (`level-works/`), no dentro de `frontend/` — de lo contrario el volumen monta una ruta con `frontend/frontend` duplicado. En PowerShell (Windows), si estás parado dentro de `frontend/`, usa `-v "${PWD}:/app"` (sin agregar `/frontend` de nuevo).