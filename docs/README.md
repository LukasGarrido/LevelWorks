# Centro de Documentación — Level Works

Bienvenido a la documentación oficial del sistema **Level Works**, una plataforma de gestión y reservas optimizada para negocios de autolavado y estética automotriz.

El proyecto está diseñado bajo una **arquitectura desacoplada API-First**:
- **Backend:** FastAPI (Python 3.12) con ORM SQLAlchemy 2.0 asíncrono y PostgreSQL 16.
- **Frontend:** Astro (TypeScript + Tailwind CSS v4) en modo estático servido por Nginx.
- **Panel Administrativo:** SQLAdmin integrado en el backend para administración interna.
- **Infraestructura:** Docker & Docker Compose para entornos de producción y desarrollo.

---

## Mapa de Navegación de la Documentación

A continuación encontrarás los enlaces a cada uno de los módulos detallados de documentación:

| Documento | Descripción | Enlace |
| :--- | :--- | :--- |
| **Arquitectura del Sistema** | Diseño técnico, patrón desacoplado, componentes del sistema y flujo de datos. | [`architecture.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/architecture.md) |
| **Especificación de la API REST** | Endpoints de `/api/v1`, contratos JSON (Pydantic), autenticación JWT y códigos HTTP. | [`api.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/api.md) |
| **Base de Datos y Modelos** | Diagrama Entidad-Relación, esquemas de tablas, índices anti-conflicto y comandos PostgreSQL. | [`database.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/database.md) |
| **Guía de Desarrollo Local** | Setup paso a paso para desarrolladores, recarga en vivo con Docker `--profile dev` y comandos útiles. | [`development.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/development.md) |
| **Guía de Despliegue en Producción** | Configuración de servidores, Nginx, SSL con Certbot, Docker Multi-Stage y variables de entorno. | [`deployment.md`](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/deployment.md) |

---

## Resumen del Proyecto

```text
level-works/
├── docs/                       # Documentación técnica centralizada
│   ├── README.md               # Índice general y guía de navegación
│   ├── architecture.md         # Arquitectura desacoplada y flujos de datos
│   ├── api.md                  # Referencia y especificación de endpoints REST API
│   ├── database.md             # Esquema relacional, ERD e índices de PostgreSQL
│   ├── development.md          # Manual para desarrolladores y entorno dev
│   └── deployment.md           # Guía de producción, Nginx, SSL y Docker
├── backend/                    # API FastAPI, SQLAdmin y Lógica de Negocio
├── frontend/                   # Aplicación Astro estática y Wizard de Reserva
└── docker-compose.yml          # Orquestación de servicios en Docker
```

Para comenzar a explorar el código o levantar el proyecto localmente, consulta la [Guía de Desarrollo Local](file:///c:/Users/lukas/Desktop/Projects/LevelWorks/docs/development.md).
