# 04 — Frontend con Jinja2 + Bootstrap

## ¿Por qué Server-Side Rendering (SSR) con Jinja2?

Se eligió renderizar HTML en el servidor con **Jinja2** (incluido en FastAPI) en
lugar de montar un frontend separado con React/Vue/TypeScript:

- **Simplicidad:** no hay build tools, bundlers ni un segundo proyecto que
  mantener y desplegar. La misma app de FastAPI sirve API y vistas.
- **Menor curva de aprendizaje:** las plantillas son HTML con pequeños bloques
  de lógica; cualquiera que sepa HTML las entiende.
- **Suficiente para un MVP:** el objetivo es visualizar y gestionar incidentes,
  no construir una SPA compleja. SSR cubre el caso de uso con menos código.
- **SEO/carga inicial:** el HTML llega ya renderizado (irrelevante aquí, pero es
  una ventaja conocida de SSR).

Cuando el proyecto crezca (interacciones ricas, tiempo real), se podría migrar
la capa de vistas a un SPA consumiendo la **misma API REST** que ya existe.

## Estructura de plantillas

| Plantilla | Rol |
|-----------|-----|
| `base.html` | Layout común: navbar, Bootstrap CDN, bloques `content` y `scripts` |
| `login.html` | Formulario de acceso; hace `fetch` a `/auth/login` y guarda el token |
| `dashboard.html` | Tabla de incidentes + 2 gráficas Chart.js |
| `incidentes.html` | Vista detallada de todos los incidentes |

Las plantillas usan **herencia** (`{% extends "base.html" %}`) y **bloques**
(`{% block content %}`), de modo que el layout (navbar, estilos, scripts) se
define una sola vez.

## Detalles de implementación

- **Bootstrap 5 por CDN** para estilos responsivos sin instalar nada.
- **Badges de severidad con color condicional** en Jinja2:
  ```jinja
  <span class="badge bg-{{ 'danger' if inc.severidad.value == 'critica'
      else 'warning' if inc.severidad.value == 'alta' else 'secondary' }}">
      {{ inc.severidad.value }}
  </span>
  ```
  Crítica → rojo, alta → amarillo, resto → gris. Comunica la prioridad de un
  vistazo.
- **CSS propio** en `app/static/style.css`, servido vía
  `app.mount("/static", StaticFiles(...))`.
- **Manejo de listas vacías** con `{% for ... %} ... {% else %} ... {% endfor %}`
  para mostrar "No hay incidentes registrados" cuando la tabla está vacía.

## Login en el cliente

`login.html` envía las credenciales como `URLSearchParams` (formato de
formulario que espera `OAuth2PasswordRequestForm`), recibe el `access_token` y
lo guarda en `localStorage`. En un entorno real se usaría una cookie `httpOnly`
(ver `docs/03-autenticacion.md`).

## Capturas sugeridas

- Pantalla de login → **`capturas/login.png`**
- Dashboard con incidentes y gráficas → **`capturas/dashboard.png`**
