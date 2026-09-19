# Level Works

**Level Works** es una plataforma moderna de gestión y reservas en línea, diseñada y optimizada para negocios de autolavado y estética automotriz.

El proyecto está desarrollado bajo una **arquitectura desacoplada y escalable**, compuesta por un backend API-first asíncrono con **FastAPI** y un frontend de alto rendimiento construido con **Astro**, totalmente contenedorizado mediante **Docker**.

---

## Características Principales

- **Experiencia de Reserva Fluida:** Wizard interactivo de agendamiento en 3 pasos (Servicio $\rightarrow$ Fecha y Hora $\rightarrow$ Confirmación) integrado en la Landing Page.
- **Backend API-First:** API REST pura construida con FastAPI (Python 3.12) y ORM asíncrono SQLAlchemy 2.0.
- **Prevención de Conflictos de Horario:** Índice condicional único en PostgreSQL que previene reservas duplicadas a nivel de base de datos.
- **Panel Administrativo Interno:** Gestión de servicios, clientes, usuarios y reservas a través de SQLAdmin expuesto en `/admin`.
- **Despliegue Flexible:** Entorno multi-contenedor dockerizado con soporte para desarrollo con hot-reload (`--profile dev`) y producción servido por Nginx.

---

## Inicio Rápido

### Prerrequisitos
- [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados.

### 1. Clonar el repositorio y configurar entorno
```bash
git clone https://github.com/LukasGarrido/LevelWorks.git
cd LevelWorks
cp .env.example .env
```

### 2. Levantar el proyecto

**Modo Desarrollo (con hot-reload):**
```bash
docker compose --profile dev up --build
```
- Frontend: `http://localhost:4323`
- Backend API: `http://localhost:8001/api/v1`
- Swagger UI: `http://localhost:8001/docs`

**Modo Producción:**
```bash
docker compose up -d --build
```
- Frontend (Nginx): `http://localhost:4323`
- Backend API: `http://localhost:8000/api/v1`

---

## Documentación del Proyecto

Para obtener información detallada sobre la arquitectura, la API, la base de datos o guías paso a paso, consulte los módulos en el directorio [`docs/`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs):

| Documento | Descripción |
| :--- | :--- |
| [`docs/README.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/README.md) | **Centro de Documentación** — Mapa general e índice navegable. |
| [`docs/architecture.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/architecture.md) | **Arquitectura del Sistema** — Patrón desacoplado, diagrama de componentes y flujos de datos. |
| [`docs/api.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/api.md) | **Especificación de la API REST** — Endpoints `/api/v1`, contratos JSON, payloads y autenticación JWT. |
| [`docs/database.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/database.md) | **Modelo de Base de Datos** — Diagrama ERD, tablas, relaciones e índices condicionales anti-conflicto. |
| [`docs/development.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/development.md) | **Guía de Desarrollo Local** — Setup de entorno dev, recarga en vivo con Docker y estándares de código. |
| [`docs/deployment.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/deployment.md) | **Guía de Despliegue en Producción** — Configuración en VPS, Nginx Reverse Proxy, SSL y respaldos. |