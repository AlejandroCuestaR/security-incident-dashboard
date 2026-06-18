
# Security Incident Dashboard

Aplicacion Full Stack para gestion de incidentes de seguridad: registro, clasificacion por severidad, seguimiento de estado y metricas visuales, mapeado a tecnicas MITRE ATT&CK.

## Objetivo
Sistema de gestion de incidentes de seguridad que permite a un equipo SOC registrar, clasificar y dar seguimiento a alertas, con metricas visuales de severidad, estado y tecnicas MITRE.

## Stack tecnologico
- Backend: FastAPI + SQLAlchemy
- Base de datos: MySQL 8
- Autenticacion: JWT (OAuth2 Password Flow)
- Frontend: Jinja2 (SSR) + Bootstrap 5 + Chart.js
- Infraestructura: Docker + Docker Compose + Microsoft Azure
- Documentacion de API: OpenAPI / Swagger (automatica en /docs)

## Como ejecutarlo

### Opcion A - Docker
git clone https://github.com/AlejandroCuestaR/security-incident-dashboard.git
cd security-incident-dashboard
cp .env.example .env
docker compose up --build

Visita:
- http://localhost:8000/ - login
- http://localhost:8000/dashboard - dashboard con metricas
- http://localhost:8000/docs - documentacion Swagger

## Funcionalidades
- CRUD completo de incidentes
- Autenticacion JWT con usuarios y roles
- Dashboard con metricas por severidad y estado (Chart.js)
- Metricas adicionales por tecnica MITRE
- Integracion con Wazuh
- Documentacion automatica OpenAPI / Swagger

## Capturas

### Login
![Login](capturas/login.png)

### Dashboard
![Dashboard](capturas/dashboardv0.png)

### Documentacion Swagger
![Swagger](capturas/swaggerv2.png)

## Documentacion detallada
Ver carpeta docs/ para arquitectura, modelo de datos, API, autenticacion, frontend, metricas, docker y despliegue en Azure.

## Autor
Alejandro Cuesta Rodriguez - Ingeniero en Sistemas Computacionales
'@
