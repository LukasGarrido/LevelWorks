# Xperience

Un sistema de gestión y reserva de citas optimizado para negocios de autolavado. Desarrollado bajo una arquitectura de monolito moderno para evitar la sobrecarga de frameworks frontend pesados, garantizando un rendimiento ultrarrápido y un despliegue simplificado.

## Stack Tecnológico (Opción B)

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
* **Frontend Reactivo:** [HTMX](https://htmx.org/) + HTML5 puro (Sin Node.js, Webpack o Vite)
* **Estilos:** [Tailwind CSS](https://tailwindcss.com/)
* **Base de Datos:** SQLite / PostgreSQL (Vía SQLAlchemy)
* **Infraestructura:** Docker & Docker Compose

---

## Estructura del Proyecto

```text
xperience/
├── .env                          # Variables de entorno (actualizado con DB_HOST/DB_PORT)
├── .gitignore                    # Reglas completas para Python, IDEs, Docker
├── Dockerfile                    # Imagen Python 3.12-slim + uvicorn con hot-reload
├── docker-compose.yml            # PostgreSQL 16 + App web con healthcheck
├── requirements.txt              # Tus dependencias + pydantic-settings añadido
├── README.md
└── app/
    ├── __init__.py
    ├── config.py                 # Configuración centralizada (pydantic-settings + .env)
    ├── database.py               # Engine async SQLAlchemy + sesión + init_db()
    ├── main.py                   # Punto de entrada FastAPI (lifespan, routers)
    ├── models.py                 # Client, Service, Reservation (con enum de estados)
    ├── routes/
    │   ├── __init__.py
    │   ├── views.py              # Rutas HTML (página principal)
    │   └── api.py                # Endpoints HTMX (con ejemplo comentado)
    └── templates/
        ├── base.html             # Esqueleto HTML (Tailwind CDN + HTMX)
        ├── index.html            # Página de reservas (con guía de HTMX inline)
        └── components/
            └── horas_disponibles.html  # Fragmento HTMX para horas libres