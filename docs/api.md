# Especificación de la API REST — Level Works

La API REST de **Level Works** está versionada bajo el prefijo `/api/v1`. Toda la comunicación se realiza mediante **JSON** utilizando codificación UTF-8.

---

## 1. Información General

- **Base URL:** `http://localhost:8000/api/v1` (o según variable `PUBLIC_API_URL`)
- **Documentación Interactiva (Swagger UI):** `http://localhost:8000/docs`
- **Documentación ReDoc:** `http://localhost:8000/redoc`

---

## 2. Autenticación

Los endpoints protegidos (uso administrativo) requieren una cabecera HTTP `Authorization` con un token JWT válido:

```http
Authorization: Bearer <access_token>
```

Para obtener un token, envíe una petición `POST` al endpoint `/auth/login`.

---

## 3. Endpoints por Módulo

### 3.1 Autenticación (`/auth`)

#### `POST /auth/login`
Autentica un usuario administrativo y retorna un JWT access token.

- **Acceso:** Público
- **Content-Type:** `application/x-www-form-urlencoded` o `application/json`
- **Body de Solicitud:**
  ```json
  {
    "username": "admin",
    "password": "mi_contraseña_segura"
  }
  ```
- **Respuesta Exitosa (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

---

### 3.2 Catálogo de Servicios (`/services`)

#### `GET /services/`
Obtiene la lista de servicios de lavado activos.

- **Acceso:** Público
- **Respuesta Exitosa (200 OK):**
  ```json
  [
    {
      "id": 1,
      "name": "Lavado Completo Premium",
      "description": "Lavado exterior a presión, aspirado profundo de interiores y silicona de neumáticos.",
      "price": 25000.0,
      "photo": "/img/servicios/lavado-premium.jpg",
      "duration_minutes": 45,
      "is_active": true,
      "created_at": "2026-09-19T14:30:00Z"
    }
  ]
  ```

#### `GET /services/{id}`
Obtiene el detalle de un servicio por su ID.

- **Acceso:** Público
- **Respuesta Exitosa (200 OK):** Mismo formato de un objeto `Service`.
- **Respuesta Error (404 Not Found):** `{"detail": "Servicio no encontrado"}`

#### `POST /services/`
Crea un nuevo servicio en el catálogo.

- **Acceso:** Requerido Admin (JWT)
- **Body de Solicitud:**
  ```json
  {
    "name": "Tratamiento Cerámico",
    "description": "Protección de pintura de alta durabilidad.",
    "price": 120000.0,
    "duration_minutes": 120,
    "is_active": true
  }
  ```
- **Respuesta Exitosa (201 Created):** Objeto `Service` creado.

#### `PUT /services/{id}`
Edita un servicio existente.

- **Acceso:** Requerido Admin (JWT)
- **Body de Solicitud:** Atributos del servicio a actualizar.
- **Respuesta Exitosa (200 OK):** Objeto `Service` actualizado.

#### `DELETE /services/{id}`
Elimina un servicio del catálogo.

- **Acceso:** Requerido Admin (JWT)
- **Respuesta Exitosa (204 No Content)**

---

### 3.3 Reservas y Disponibilidad (`/reservations`)

#### `POST /reservations/`
Crea una nueva reserva. Registra o vincula automáticamente los datos del cliente.

- **Acceso:** Público
- **Body de Solicitud:**
  ```json
  {
    "service_id": 1,
    "scheduled_at": "2026-09-20T10:00:00Z",
    "client": {
      "name": "Carlos Mendoza",
      "email": "carlos.mendoza@email.com",
      "phone": "+56912345678"
    },
    "vehicle": "SUV Mazda CX-5 (Gris)",
    "notes": "Atención especial a llantas de aleación."
  }
  ```
- **Respuesta Exitosa (201 Created):**
  ```json
  {
    "id": 15,
    "client_id": 4,
    "service_id": 1,
    "scheduled_at": "2026-09-20T10:00:00Z",
    "status": "pendiente",
    "vehicle": "SUV Mazda CX-5 (Gris)",
    "notes": "Atención especial a llantas de aleación.",
    "created_at": "2026-09-19T17:00:00Z",
    "client": {
      "id": 4,
      "name": "Carlos Mendoza",
      "email": "carlos.mendoza@email.com",
      "phone": "+56912345678"
    },
    "service": {
      "id": 1,
      "name": "Lavado Completo Premium",
      "price": 25000.0,
      "duration_minutes": 45
    }
  }
  ```
- **Errores Posibles:**
  - `404 Not Found`: Servicio especificado no existe.
  - `409 Conflict`: El bloque horario solicitado ya está reservado.

#### `GET /reservations/`
Lista todas las reservas registradas.

- **Acceso:** Requerido Admin (JWT)
- **Respuesta Exitosa (200 OK):** Array de objetos `ReservationResponseSchema`.

#### `PATCH /reservations/{id}/status`
Actualiza únicamente el estado de una reserva.

- **Acceso:** Requerido Admin (JWT)
- **Estados Válidos:** `pendiente`, `confirmada`, `en_progreso`, `completada`, `cancelada`.
- **Body de Solicitud:**
  ```json
  {
    "status": "confirmada"
  }
  ```
- **Respuesta Exitosa (200 OK):** Objeto `Reservation` actualizado.

#### `DELETE /reservations/{id}`
Elimina una reserva.

- **Acceso:** Requerido Admin (JWT)
- **Respuesta Exitosa (204 No Content)**

---

### 3.4 Clientes (`/clients`)

#### `GET /clients/`
Lista los clientes registrados automáticamente en el sistema.

- **Acceso:** Requerido Admin (JWT)
- **Respuesta Exitosa (200 OK):**
  ```json
  [
    {
      "id": 4,
      "name": "Carlos Mendoza",
      "email": "carlos.mendoza@email.com",
      "phone": "+56912345678",
      "created_at": "2026-09-19T17:00:00Z"
    }
  ]
  ```

#### `GET /clients/{id}`
Obtiene el detalle de un cliente por su ID.

- **Acceso:** Requerido Admin (JWT)

---

### 3.5 Usuarios Internos (`/users`)

#### `GET /users/`
Lista los usuarios administradores del sistema.

- **Acceso:** Requerido Admin (JWT)

#### `POST /users/`
Crea un nuevo usuario administrativo.

- **Acceso:** Requerido Admin (JWT)
- **Body de Solicitud:**
  ```json
  {
    "username": "operador1",
    "email": "operador@levelworks.cl",
    "password": "contraseña_segura",
    "rol": "editor",
    "permissions": ["leer", "actualizar"]
  }
  ```

---

## 4. Respuestas de Error Estándar

En caso de fallo, la API responde con un código de estado HTTP adecuado y una estructura JSON uniforme:

```json
{
  "detail": "Descripción clara y detallada del motivo del error"
}
```

### Códigos de Estado Frecuentes:
- `200 OK` — Operación completada con éxito.
- `201 Created` — Recurso creado exitosamente.
- `204 No Content` — Eliminación exitosa sin cuerpo de respuesta.
- `400 Bad Request` — Parámetros inválidos o error de sintaxis.
- `401 Unauthorized` — Token JWT faltante, inválido o expirado.
- `403 Forbidden` — El usuario no tiene permisos suficientes para la acción.
- `404 Not Found` — El recurso solicitado no existe.
- `409 Conflict` — Conflicto de negocio (ej. horario reservado por otro cliente).
- `422 Unprocessable Entity` — Fallo de validación Pydantic en los campos enviados.
