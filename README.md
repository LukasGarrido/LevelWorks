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
carwash-flow/
├── app/
│   ├── main.py             # Punto de entrada de FastAPI
│   ├── database.py         # Configuración de base de datos y ORM
│   ├── models.py           # Modelos relacionales (Clientes, Reservas, Servicios)
│   ├── routes/             # Endpoints (API y Vistas HTML)
│   └── templates/          # Plantillas Jinja2
│       ├── base.html       # Estructura principal
│       ├── index.html      # Pantalla de reserva del cliente
│       └── components/     # Fragmentos HTMX (ej. horas_disponibles.html)
├── Dockerfile              # Configuración de la imagen del contenedor
├── docker-compose.yml      # Orquestación de servicios
├── requirements.txt        # Dependencias de Python
└── README.md               # Documentación