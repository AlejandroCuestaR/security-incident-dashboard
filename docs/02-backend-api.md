# 02 — Backend API (FastAPI)

## Tabla de endpoints

### Autenticación (`/auth`)

| Método | Ruta | Descripción | ¿Auth? |
|--------|------|-------------|:------:|
| POST | `/auth/registro` | Registra un nuevo usuario | No |
| POST | `/auth/login` | Devuelve un token JWT | No |

### Incidentes (`/incidentes`)

| Método | Ruta | Descripción | ¿Auth? |
|--------|------|-------------|:------:|
| POST | `/incidentes/` | Crea un incidente | Sí |
| GET | `/incidentes/` | Lista todos los incidentes | Sí |
| GET | `/incidentes/{id}` | Obtiene un incidente por id | Sí |
| PATCH | `/incidentes/{id}` | Actualiza estado/severidad | Sí |
| DELETE | `/incidentes/{id}` | Elimina un incidente | Sí |
| GET | `/incidentes/metricas/severidad` | Conteo por severidad | No |
| GET | `/incidentes/metricas/estado` | Conteo por estado | No |
| GET | `/incidentes/metricas/mitre` | Conteo por técnica MITRE | No |

### Usuarios (`/usuarios`)

| Método | Ruta | Descripción | ¿Auth? |
|--------|------|-------------|:------:|
| GET | `/usuarios/me` | Perfil del usuario autenticado | Sí |
| GET | `/usuarios/` | Lista de usuarios | Sí |

### Vistas HTML

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Pantalla de login |
| GET | `/dashboard` | Dashboard con métricas |
| GET | `/incidentes-vista` | Tabla detallada de incidentes |

## Patrón de diseño

- **Router separado por recurso** (`app/routers/incidentes.py`, `usuarios.py`,
  `auth.py`). Cada `APIRouter` agrupa los endpoints de un recurso con su propio
  `prefix` y `tags`, lo que mantiene el código modular y organiza Swagger por
  secciones.
- **Esquemas Pydantic** (`app/schemas.py`) para validar la **entrada**
  (`IncidenteCreate`, `IncidenteUpdate`, `UsuarioCreate`) y dar forma a la
  **salida** (`IncidenteOut`, `UsuarioOut`). Con `response_model` FastAPI filtra
  los campos expuestos (p. ej. nunca devuelve `hashed_password`).
- **Inyección de dependencias** con `Depends`:
  - `get_db` abre y cierra la sesión de base de datos por request.
  - `get_current_user` exige y valida el token JWT en los endpoints protegidos.
- **Separación de capas:** los routers orquestan; los modelos hablan con la BD;
  los schemas validan; `auth.py` concentra la seguridad.

## Nota de implementación: orden de las rutas

Los endpoints `/incidentes/metricas/*` se declaran **antes** que
`/incidentes/{incidente_id}`. FastAPI evalúa las rutas en orden, y si
`/{incidente_id}` estuviera primero, una petición a `/incidentes/metricas/severidad`
intentaría interpretar `"metricas"` como un `id` entero y fallaría. Declarar las
rutas específicas antes que las dinámicas evita ese conflicto.

## Validación automática

Gracias a Pydantic + los `Enum` del modelo:

- Crear un incidente con `severidad: "altísima"` → **422 Unprocessable Entity**.
- Registrar un usuario con un email mal formado → **422** (validado por `EmailStr`).
- Pedir un incidente inexistente → **404 Not Found** (manejado con `HTTPException`).

## Captura sugerida

Levanta la app y abre `http://localhost:8000/docs`. Verás todos los endpoints
agrupados por tags. Guarda la captura como **`capturas/swagger.png`**.
