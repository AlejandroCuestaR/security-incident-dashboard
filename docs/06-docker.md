# 06 — Dockerización

El proyecto se empaqueta con **Docker** y se orquesta con **Docker Compose**
(dos servicios: la app y la base de datos).

## Servicios del `docker-compose.yml`

### `db` — Base de datos MySQL 8
- Imagen oficial `mysql:8.0`.
- Crea automáticamente la base `incidentes_db` y el usuario `root`.
- Persiste los datos en el volumen `db_data` (sobreviven a reinicios).
- Expone el puerto `3306` (útil para conectarte con DBeaver/MySQL Workbench).
- Tiene un **healthcheck** (`mysqladmin ping`) para avisar cuándo está lista.

### `web` — Aplicación FastAPI
- Se construye desde el `Dockerfile` (`build: .`).
- Expone el puerto `8000` (la app: `http://localhost:8000`).
- `depends_on: db (condition: service_healthy)` → **espera a que MySQL esté
  listo** antes de arrancar. Esto evita el error típico de "connection refused"
  cuando la app inicia más rápido que la base de datos.
- Recibe la configuración por variables de entorno (`DATABASE_URL`,
  `SECRET_KEY`, etc.).

## Cómo se comunican

Compose crea una red interna donde cada servicio es accesible **por su nombre**.
Por eso la app se conecta a la base de datos con el host `db`, no `localhost`:

```
DATABASE_URL: mysql+pymysql://root:rootpassword@db/incidentes_db
                                                  ↑
                                          nombre del servicio
```

```
┌─────────────────── red de docker-compose ───────────────────┐
│                                                              │
│   ┌──────────┐   mysql+pymysql://...@db    ┌─────────────┐   │
│   │   web    │ ─────────────────────────▶  │     db      │   │
│   │  :8000   │                             │   :3306     │   │
│   └────┬─────┘                             └─────────────┘   │
│        │                                          │          │
└────────┼──────────────────────────────────────────┼─────────┘
   host:8000 (navegador)                       volumen db_data
```

## Dockerfile (resumen)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- Imagen base ligera (`slim`).
- Se copia primero `requirements.txt` e instala dependencias, aprovechando la
  caché de capas de Docker (si el código cambia pero las deps no, no reinstala).
- `--host 0.0.0.0` para que el servidor sea accesible desde fuera del contenedor.

## Levantar el proyecto desde cero

```bash
docker compose up --build
```

Esto construye la imagen, arranca MySQL, espera a que esté lista, arranca la app
y crea las tablas automáticamente (`models.Base.metadata.create_all`).

Para detener y limpiar:

```bash
docker compose down          # detiene los contenedores
docker compose down -v       # además borra el volumen de datos
```

## Verificación / captura sugerida

Con los contenedores corriendo, ejecuta:

```bash
docker ps
```

Deberías ver **dos contenedores** activos (`web` y `db`). Guarda la captura como
**`capturas/docker-ps.png`**.
