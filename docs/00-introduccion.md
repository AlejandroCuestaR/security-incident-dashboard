# 00 — Introducción

## Propósito del proyecto

> *Sistema de gestión de incidentes de seguridad que permite a un equipo SOC
> (Security Operations Center) registrar, clasificar y dar seguimiento a alertas,
> con métricas visuales de severidad y técnicas MITRE.*

El objetivo es demostrar un stack de desarrollo Full Stack moderno (FastAPI +
MySQL + JWT + Docker + Azure) aplicado a un caso de uso real de ciberseguridad:
la operación diaria de un analista SOC que necesita un lugar único donde
documentar incidentes, priorizarlos por severidad y medir tendencias.

## Contexto de uso

Un analista SOC recibe alertas de múltiples fuentes (SIEM, EDR, firewalls,
Wazuh, etc.). Este dashboard centraliza esas alertas como **incidentes**, les
asigna una **severidad** (baja, media, alta, crítica), un **estado** del ciclo de
vida (abierto, en progreso, cerrado) y, opcionalmente, la **técnica MITRE
ATT&CK** asociada (por ejemplo `T1566` para phishing). Con esa información el
equipo puede priorizar y tomar decisiones basadas en métricas.

## Arquitectura

```
┌──────────────┐      HTTP       ┌────────────────────┐     SQL      ┌───────────┐
│   Cliente    │ ──────────────▶ │      FastAPI       │ ───────────▶ │   MySQL   │
│ (navegador)  │ ◀────────────── │ (API REST + Jinja2)│ ◀─────────── │           │
└──────────────┘   HTML / JSON   └────────────────────┘   resultados └───────────┘
        │                                  │
        │  Chart.js consume /incidentes/metricas/*  (JSON)
        └───────────────────────────────────────────┘
```

- **Cliente (navegador):** renderiza el HTML que entrega FastAPI vía Jinja2 y
  consume los endpoints de métricas con `fetch` para dibujar las gráficas con
  Chart.js.
- **FastAPI:** capa de aplicación. Expone una API REST (CRUD + métricas +
  autenticación) y además sirve vistas HTML renderizadas en el servidor.
- **MySQL:** capa de persistencia. Almacena usuarios, incidentes y logs de
  actividad.

## Capas del proyecto

| Capa | Responsabilidad | Archivos |
|------|-----------------|----------|
| Presentación | Vistas HTML + gráficas | `app/templates/`, `app/static/` |
| API / Aplicación | Endpoints REST y lógica | `app/main.py`, `app/routers/` |
| Seguridad | Autenticación y hashing | `app/auth.py` |
| Validación | Esquemas de entrada/salida | `app/schemas.py` |
| Datos | Modelos y conexión | `app/models.py`, `app/database.py` |

## Decisiones de diseño clave

- **Server-Side Rendering con Jinja2** en lugar de un SPA (React/Vue): menor
  complejidad, suficiente para un MVP y permite enfocar el esfuerzo en el backend.
- **JWT (OAuth2)** para autenticación stateless, estándar de la industria.
- **Docker Compose** para reproducir el entorno completo (app + base de datos)
  con un solo comando.
