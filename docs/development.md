# Guía de Desarrollo Local — Level Works

Esta guía describe el procedimiento paso a paso para configurar el entorno de desarrollo local del proyecto **Level Works**.

---

## 1. Requisitos del Sistema

- **Docker Desktop** (versión 20.10+) y **Docker Compose v2+**.
- **Git**.
- *(Opcional)* Node.js v22+ o Python 3.12+ si desea ejecutar herramientas de formateo de código directamente en el host sin Docker.

> **Nota sobre la Arquitectura Dockerizada:** No requiere instalar Node.js, Python ni PostgreSQL localmente. Todo el stack ejecuta dentro de contenedores optimizados.

---

## 2. Configuración Inicial del Proyecto

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/LukasGarrido/LevelWorks.git
cd LevelWorks
```

### Paso 2: Crear el archivo de variables de entorno
Copie el archivo de ejemplo para generar el `.env` local:
```bash
cp .env.example .env
```

Contenido sugerido para desarrollo local (`.env`):
```env
# Aplicación
APP_NAME=Level Works (Dev)
DEBUG=True
SECRET_KEY=password_desarrollo_secret_key_12345

# Backend (API)
PORT=8000
PORT_DEV=8001
CORS_ORIGINS=http://localhost:4323,http://localhost:4321,http://127.0.0.1:4323

# Frontend (Astro)
FRONTEND_PORT=4323
PUBLIC_API_URL=http://localhost:8001/api/v1

# Base de Datos PostgreSQL
DB_NAME=levelworks_db
DB_USER=postgres
DB_PASSWORD=123
DB_PORT=5432

# Contacto (Modales & Footer)
CONTACT_EMAIL=contacto@levelworks.cl
CONTACT_PHONE=+56912345678
INSTAGRAM_HANDLE=@levelworks
```

---

## 3. Ejecución del Entorno de Desarrollo (Hot-Reload)

Para desarrollar con recarga en vivo al guardar cualquier cambio en los archivos de código fuente, ejecute el perfil `dev`:

```bash
docker compose --profile dev up --build
```

### Servicios desplegados en desarrollo:
- **`db`** — Contenedor PostgreSQL 16 escrutando en `localhost:5432`.
- **`api-dev`** — Backend FastAPI corriendo en Uvicorn con `--reload` en `http://localhost:8001`.
- **`frontend-dev`** — Astro Dev Server escuchando en `http://localhost:4323` con recarga automática por volumen.

---

## 4. Crear Superusuario Administrador

Una vez levantado el entorno por primera vez, inicialice la cuenta administradora ejecutando el script CLI en el contenedor de la API:

```bash
docker exec -it levelworks-api-dev-1 python create_admin.py
```

Siga las instrucciones en la terminal para definir el usuario y contraseña del administrador.

---

## 5. Accesos Rápidos en Desarrollo

| Servicio | URL de Acceso | Descripción |
| :--- | :--- | :--- |
| **Frontend Astro Dev** | `http://localhost:4323` | Aplicación web dinámica con hot-reload |
| **FastAPI Dev API** | `http://localhost:8001/api/v1` | Endpoints JSON de desarrollo |
| **Swagger UI (Docs)** | `http://localhost:8001/docs` | Documentación interactiva de la API |
| **Panel SQLAdmin** | `http://localhost:8001/admin` | Panel de gestión interna de datos |

---

## 6. Estándares y Flujo de Trabajo

### Backend (FastAPI)
1. **Modelos ORM (`app/models/`):** Al añadir una nueva tabla o columna, agréguela en el modelo correspondiente derivado de `Base`.
2. **Esquemas Pydantic (`app/schemas/`):** Defina los esquemas de solicitud (`CreateSchema`, `UpdateSchema`) y de respuesta (`ResponseSchema`).
3. **Servicios (`app/services/`):** Escriba la lógica de negocio como funciones asíncronas puras (`async def`).
4. **Endpoints (`app/api/v1/`):** Registre las rutas HTTP del controlador invocando los servicios y manejando las excepciones HTTP pertinentes.

### Frontend (Astro)
1. **Estilos:** Utilice clases de utilidad de **Tailwind CSS v4** directamente en el HTML de los componentes `.astro`.
2. **Tipos:** Sincronice las interfaces de datos en `src/lib/types.ts` con los esquemas Pydantic del backend.
3. **Peticiones HTTP:** Use `lib/api.ts` para centralizar los llamadas `fetch` tipadas al backend.

---

## 7. Comandos de Limpieza y Reinicio

### Reiniciar el entorno de desarrollo desde cero (limpiando datos):
```bash
docker compose --profile dev down -v
docker compose --profile dev up --build
```

### Ver logs en tiempo real:
```bash
docker compose logs -f api-dev
docker compose logs -f frontend-dev
```
