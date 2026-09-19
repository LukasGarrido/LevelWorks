# Level Works

Sistema de gestión y reserva, optimizado para negocios de autolavado. Desarrollado bajo una **arquitectura desacoplada**: un backend API-first construido con FastAPI y un frontend independiente construido con Astro, comunicados vía REST/JSON.

---

## Stack Tecnológico

### Backend (API)

| Tecnología | Versión | Breve Descripción |
| :--- | :--- | :--- |
| **FastAPI** | 0.110+ (Python 3.12) | Framework backend asíncrono de alto rendimiento, expuesto como API JSON pura bajo `/api/v1`. |
| **SQLAlchemy** | 2.0+ | ORM asíncrono (`asyncpg`) para la gestión y modelado relacional de datos. |
| **PostgreSQL** | 16 | Base de datos relacional principal para entornos de producción y desarrollo. |
| **Pydantic** | 2.x | Contratos de entrada/salida tipados (schemas) para cada endpoint de la API. |
| **PyJWT & Passlib / Bcrypt** | — | Autenticación basada en JWT y hashing seguro de contraseñas. |
| **SQLAdmin** | 0.17+ | Panel de administración integrado (SSR interno para gestión de datos, desacoplado del frontend). |
| **fastapi-storages & Pillow** | 0.3+ / 10.0+ | Almacenamiento y gestión de imágenes para SQLAdmin. |

### Frontend

| Tecnología | Versión | Breve Descripción |
| :--- | :--- | :--- |
| **Astro** | 5.x / 7.x | Framework frontend estático (`output: 'static'`). Despliegue de alto rendimiento servido con Nginx. |
| **Tailwind CSS** | 4.x | Framework CSS utility-first, integrado mediante `@tailwindcss/vite`. |
| **tw-animate-css** | 1.x | Utilidades de animación compatibles con Tailwind v4. |
| **TypeScript** | strict | Tipado del cliente API (`lib/api.ts`, `lib/types.ts`) e interfaces del sistema. |

### Infraestructura

| Tecnología | Versión | Breve Descripción |
| :--- | :--- | :--- |
| **Docker & Docker Compose** | v2+ | Contenedorización y orquestación de backend, frontend y base de datos con perfiles para producción y desarrollo (`--profile dev`). |
| **nginx** | alpine | Servidor web ultraligero que sirve el build estático de Astro en producción. |

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
│   │   ├── Dockerfile                  # Imagen de producción (Uvicorn asíncrono)
│   │   └── Dockerfile.dev              # Imagen de desarrollo (Uvicorn --reload)
│   ├── requirements.txt
│   ├── create_admin.py                 # Script CLI para inicializar superusuario admin
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py                     # FastAPI app, CORS, SQLAdmin views, static mount /img
│       ├── auth.py                     # Backend de autenticación para SQLAdmin
│       ├── config.py                   # Pydantic Settings (variables de entorno)
│       │
│       ├── core/
│       │   ├── security.py             # Hashing y verificación de contraseñas
│       │   ├── jwt.py                  # Generación y decodificación de JWT
│       │   ├── storage.py              # Gestión de almacenamiento local de imágenes
│       │   └── db/
│       │       └── database.py         # Motor async SQLAlchemy, Session local, init_db
│       │
│       ├── models/                     # Modelos ORM (Tablas PostgreSQL)
│       │   ├── user.py
│       │   ├── client.py
│       │   ├── service.py
│       │   └── reservation.py
│       │
│       ├── schemas/                    # DTOs y validación Pydantic
│       │   ├── auth.py
│       │   ├── user.py
│       │   ├── client.py
│       │   ├── service.py
│       │   └── reservation.py
│       │
│       ├── services/                   # Capa de lógica de negocio aislada
│       │   ├── auth_service.py
│       │   ├── catalog_service.py
│       │   ├── reservation_service.py
│       │   └── user_service.py
│       │
│       ├── api/                        # Controladores y rutas HTTP
│       │   ├── deps.py                 # Inyección de dependencias (DB Session, Admin Auth)
│       │   └── v1/                     # API versionada (`/api/v1`)
│       │       ├── __init__.py         # Router principal v1
│       │       ├── auth.py
│       │       ├── users.py
│       │       ├── clients.py
│       │       ├── services.py
│       │       └── reservations.py
│       │
│       └── img/                        # Almacenamiento local de fotografías de servicios
│
└── frontend/
    ├── docker/
    │   ├── Dockerfile                  # Build multi-stage + nginx (Producción)
    │   └── Dockerfile.dev              # Node 22 + astro dev con hot-reload (Desarrollo)
    ├── astro.config.mjs
    ├── package.json
    ├── package-lock.json
    ├── tsconfig.json
    │
    ├── public/
    │   └── favicon.svg
    │
    └── src/
        ├── assets/                     # Recursos gráficos vectoriales (SVGs)
        ├── styles/
        │   └── global.css              # Directivas Tailwind CSS v4 y estilos globales
        │
        ├── lib/
        │   ├── api.ts                  # Cliente HTTP tipado para interactuar con `/api/v1`
        │   └── types.ts                # Tipos e interfaces TypeScript del frontend
        │
        ├── layouts/
        │   └── Layout.astro            # Layout principal con Meta tags, Header y Footer
        │
        ├── components/
        │   ├── layout/                 # Estructura general de página
        │   │   ├── Header.astro        # Barra de navegación superior dinámica
        │   │   └── Footer.astro        # Pie de página y modales informativos
        │   │
        │   ├── ui/                     # Componentes atómicos de interfaz reutilizables
        │   │   ├── Button.astro        # Botones estandarizados
        │   │   ├── Modal.astro         # Diálogos modales
        │   │   └── ServiceCard.astro   # Tarjetas de visualización de servicios
        │   │
        │   └── sections/               # Secciones modulares de la Landing Page
        │       ├── Hero.astro          # Sección principal / Presentación
        │       ├── HowItWorks.astro    # Guía paso a paso del servicio
        │       ├── Services.astro      # Catálogo interactivo de servicios
        │       ├── Features.astro      # Características clave / Ventajas
        │       ├── CallToAction.astro  # Banner de llamado a la acción
        │       └── BookingWizard.astro # Wizard de agendamiento en 3 pasos
        │
        └── pages/
            ├── index.astro             # Experiencia Landing Page Single Page
            └── 404.astro               # Página de error 404 personalizada
```

---

## Arquitectura del Frontend (Astro)

El frontend está diseñado bajo un enfoque de **Landing Page dinámica interactiva (SPA Experience)** construida con Astro. Toda la interactividad client-side se gestiona mediante Scripts nativos TypeScript embebidos de manera limpia en los componentes:

### Flujo del Wizard de Reserva (`BookingWizard.astro`)

El flujo completo de reservas está encapsulado en un wizard modular de 3 pasos dentro de `BookingWizard.astro`:

```text
[ Paso 1: Selección de Servicio ] ──▶ [ Paso 2: Selección de Fecha y Hora ] ──▶ [ Paso 3: Datos del Cliente ] ──▶ [ Confirmación Modal ]
       GET /api/v1/services                 GET /api/v1/reservations/availability           POST /api/v1/reservations
```

1. **Paso 1 (Servicio):** Obtiene dinámicamente el catálogo de servicios desde `GET /api/v1/services` a través de `lib/api.ts`.
2. **Paso 2 (Fecha y Horario):** Consulta los bloques horarios disponibles llamando a la API de disponibilidad en tiempo real.
3. **Paso 3 (Datos del Cliente):** Recopila la información personal y del vehículo, enviando la solicitud a `POST /api/v1/reservations`. Al completarse con éxito, se despliega una ventana modal de confirmación sin recargar la página.

### Generación y Renderizado
* **Output:** `output: 'static'` en `astro.config.mjs`. En producción, Astro genera archivos HTML/CSS/JS optimizados servidos eficientemente por **Nginx**.
* **Integración API:** Todas las interacciones dinámicas en el navegador se conectan al backend FastAPI mediante `lib/api.ts`.

---

## Cómo Levantarlo

### Prerrequisitos

* [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados. **No requiere Node.js ni Python instalados en el host**.

---

### Configurar variables de entorno

```bash
cp .env.example .env
```

Configuración predeterminada sugerida en `.env`:
```env
# Aplicación
APP_NAME=Level Works
DEBUG=True
SECRET_KEY=password

# Backend (API)
PORT=8000
CORS_ORIGINS=http://localhost:4323,http://localhost:4321

# Frontend (Astro)
FRONTEND_PORT=4323
PUBLIC_API_URL=http://localhost:8000/api/v1

# Base de Datos
DB_NAME=levelworks_db
DB_USER=postgres
DB_PASSWORD=123
DB_PORT=5432

# Información de Contacto
CONTACT_EMAIL=contacto@levelworks.cl
CONTACT_PHONE=+56912345678
INSTAGRAM_HANDLE=@levelworks
```

---

### Entorno de Producción (Stack Completo)

Para compilar e inicie todos los servicios optimizados para producción:

```bash
docker compose up -d --build
```

Servicios desplegados:
* `db` — PostgreSQL 16
* `api` — Backend FastAPI expuesto en `http://localhost:8000`
* `frontend` — Build estático de Astro servido por Nginx en `http://localhost:4323`

**Crear superusuario Administrador:**
```bash
docker exec -it levelworks-api-1 python create_admin.py
```

---

### Entorno de Desarrollo (Hot-Reload)

Para desarrollar con recarga en vivo en frontend y backend, utilice el perfil `dev`:

```bash
docker compose --profile dev up --build
```

Servicios en modo desarrollo:
* `api-dev` — FastAPI con `--reload` habilitado en `http://localhost:8001`
* `frontend-dev` — Astro Dev Server con hot-reload en `http://localhost:4323`

---

## Panel Administrativo y API

* **Sitio Web Principal:** [http://localhost:4323](http://localhost:4323)
* **Documentación Interactiva Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Documentación ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Panel de Administración SQLAdmin:** [http://localhost:8000/admin](http://localhost:8000/admin)

### Resumen de Endpoints API (`/api/v1`)

| Módulo | Endpoint | Método | Descripción | Acceso |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `/auth/login` | `POST` | Autenticación y obtención de token JWT | Público |
| **Services** | `/services/` | `GET` | Lista el catálogo de servicios activos | Público |
| **Services** | `/services/` | `POST` | Crea un nuevo servicio | Admin |
| **Services** | `/services/{id}` | `PUT` / `DELETE` | Modifica o elimina un servicio | Admin |
| **Reservations** | `/reservations/` | `POST` | Crea una nueva reserva | Público |
| **Reservations** | `/reservations/` | `GET` | Lista todas las reservas agendadas | Admin |
| **Reservations** | `/reservations/{id}/status` | `PATCH` | Actualiza el estado de una reserva | Admin |
| **Clients** | `/clients/` | `GET` | Lista clientes registrados | Admin |
| **Users** | `/users/` | `GET` / `POST` | Gestión de usuarios del sistema | Admin |

---

## Comandos de Gestión PostgreSQL

Para interactuar con la base de datos dentro del contenedor:

```bash
docker exec -it levelworks-db-1 psql -U postgres -d levelworks_db
```

Comandos útiles dentro de `psql`:
* `\dt` — Lista todas las tablas.
* `\d reservations` — Detalle de columnas e índices de una tabla.
* `\l` — Lista las bases de datos en el servidor.

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