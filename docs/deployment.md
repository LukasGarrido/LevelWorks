# Guía de Despliegue en Producción — Level Works

Esta guía detalla el procedimiento para desplegar la plataforma **Level Works** en un entorno de producción (servidor VPS, nube o infraestructura on-premise) utilizando Docker, Nginx y certificados SSL con Certbot.

---

## 1. Arquitectura de Producción

En producción, el stack corre totalmente aislado mediante Docker Compose:

```text
                               ┌─────────────────────────────────────────┐
                               │            Nginx Host Proxy             │
                               │        (Port 80 HTTP / 443 HTTPS)       │
                               └────────────────────┬────────────────────┘
                                                    │
                   ┌────────────────────────────────┴────────────────────────────────┐
                   │                                                                 │
                   ▼                                                                 ▼
 ┌───────────────────────────────────┐                             ┌───────────────────────────────────┐
 │   docker: frontend (Nginx Alpine)  │                             │      docker: api (FastAPI)        │
 │   Port 4323 (Estático Astro)      │                             │   Port 8000 (API & SQLAdmin)      │
 └───────────────────────────────────┘                             └─────────────────┬─────────────────┘
                                                                                     │
                                                                                     ▼
                                                                   ┌───────────────────────────────────┐
                                                                   │       docker: db (Postgres 16)    │
                                                                   │            Port 5432              │
                                                                   └───────────────────────────────────┘
```

---

## 2. Preparación del Servidor

### Requisitos Mínimos Recomendados:
- **SO:** Ubuntu 22.04 / 24.04 LTS o Debian 12.
- **Hardware:** 2 vCPU, 2 GB RAM, 25 GB SSD.
- **Software:** Docker Engine 24+ y Docker Compose v2+.

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/LukasGarrido/LevelWorks.git /var/www/levelworks
cd /var/www/levelworks
```

---

## 3. Variables de Entorno de Producción

Cree el archivo `.env` configurando credenciales de alta seguridad:

```bash
cp .env.example .env
nano .env
```

### Configuración obligatoria para Producción:
```env
# Aplicación
APP_NAME=Level Works
DEBUG=False
SECRET_KEY=CLAVE_SUPER_SECRETA_Y_ALEATORIA_GENERADA_CON_OPENSSL

# Backend (API)
PORT=8000
CORS_ORIGINS=https://midominio.cl,https://www.midominio.cl

# Frontend (Astro)
FRONTEND_PORT=4323
PUBLIC_API_URL=https://api.midominio.cl/api/v1

# Base de Datos PostgreSQL
DB_NAME=levelworks_prod_db
DB_USER=levelworks_user
DB_PASSWORD=PASSWORD_POSTGRES_DE_ALTA_COMPLEJIDAD
DB_PORT=5432

# Información de Contacto
CONTACT_EMAIL=contacto@midominio.cl
CONTACT_PHONE=+56912345678
INSTAGRAM_HANDLE=@levelworks
```

> **Generación de `SECRET_KEY` segura:**
> Execute `openssl rand -hex 32` en el servidor y pegue la salida como valor de `SECRET_KEY`.

---

## 4. Compilación y Despliegue con Docker Compose

Ejecute el comando de compilación e inicio en segundo plano:

```bash
docker compose up -d --build
```

### Inicializar Usuario Administrador
Una vez iniciados los servicios, cree la cuenta de administración inicial:

```bash
docker exec -it levelworks-api-1 python create_admin.py
```

---

## 5. Configuración de Reverse Proxy Nginx & SSL (Certbot)

Para servir la aplicación bajo un dominio propio con HTTPS, instale y configure Nginx en el sistema operativo host.

### Paso 1: Instalar Nginx y Certbot
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Paso 2: Crear Configuración de Nginx
Cree el archivo `/etc/nginx/sites-available/levelworks.conf`:

```nginx
server {
    server_name midominio.cl www.midominio.cl;

    # Frontend Astro (Nginx Docker)
    location / {
        proxy_pass http://127.0.0.1:4323;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    server_name api.midominio.cl;

    # Backend FastAPI REST & SQLAdmin
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Habilite el sitio y verifique la sintaxis:
```bash
sudo ln -s /etc/nginx/sites-available/levelworks.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Paso 3: Generar Certificados SSL Gratuitos con Let's Encrypt
```bash
sudo certbot --nginx -d midominio.cl -d www.midominio.cl -d api.midominio.cl
```

---

## 6. Estrategia de Respaldos de Base de Datos

Programe un script en `cron` para respaldar diariamente la base de datos PostgreSQL:

### Script de Respaldo (`/var/www/levelworks/scripts/backup.sh`)
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/levelworks"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker exec levelworks-db-1 pg_dump -U levelworks_user -d levelworks_prod_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Conservar únicamente respaldos de los últimos 30 días
find $BACKUP_DIR -type f -mtime +30 -name "*.sql.gz" -delete
```

Otorgue permisos de ejecución:
```bash
chmod +x /var/www/levelworks/scripts/backup.sh
```

Añada la tarea a `crontab -e` (ejecutar cada medianoche):
```cron
0 0 * * * /var/www/levelworks/scripts/backup.sh
```
