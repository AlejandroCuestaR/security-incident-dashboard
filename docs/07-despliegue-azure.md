# 07 — Despliegue en Azure

Despliegue de la imagen en **Azure Container Registry (ACR)** +
**Azure Container Instances (ACI)**.

> ⚠️ Los comandos no incluyen credenciales reales. Sustituye `mi-grupo`,
> `miregistroacr` y los valores de las variables de entorno por los tuyos.

## Requisitos previos

- Cuenta de Azure y [Azure CLI](https://learn.microsoft.com/cli/azure/) instalado.
- Sesión iniciada: `az login`.
- Un grupo de recursos: `az group create --name mi-grupo --location eastus`.

## 1) Crear el Container Registry y subir la imagen

```bash
# Crear el registro
az acr create --resource-group mi-grupo --name miregistroacr --sku Basic

# Autenticarse contra el registro
az acr login --name miregistroacr

# Etiquetar la imagen local apuntando al registro
docker tag security-dashboard miregistroacr.azurecr.io/security-dashboard:v1

# Subir la imagen
docker push miregistroacr.azurecr.io/security-dashboard:v1
```

> La imagen local `security-dashboard` se obtiene de
> `docker build -t security-dashboard .` (o del nombre que genere
> `docker compose build`).

## 2) Crear el Container Instance

```bash
az container create --resource-group mi-grupo --name security-dashboard \
  --image miregistroacr.azurecr.io/security-dashboard:v1 \
  --cpu 1 --memory 1 --ports 8000 \
  --registry-login-server miregistroacr.azurecr.io \
  --registry-username <usuario-acr> \
  --registry-password <password-acr> \
  --environment-variables \
      DATABASE_URL="mysql+pymysql://usuario:password@<host-mysql>/incidentes_db" \
      SECRET_KEY="<clave-secreta-larga>" \
      ALGORITHM="HS256" \
      ACCESS_TOKEN_EXPIRE_MINUTES="60"
```

> Para no exponer secretos en la línea de comandos puedes usar
> `--secure-environment-variables` para `SECRET_KEY` y la contraseña de la BD.

## 3) Obtener la IP pública y verificar

```bash
az container show --resource-group mi-grupo --name security-dashboard \
  --query ipAddress.ip --output tsv
```

Abre `http://<IP_PUBLICA>:8000/docs` y verifica que la API responde.

## Base de datos en producción

> ⚠️ En producción **no** uses un contenedor MySQL efímero. Crea una
> **Azure Database for MySQL** (servicio gestionado: backups, alta
> disponibilidad, parches) y apunta `DATABASE_URL` a ese host:

```bash
az mysql flexible-server create \
  --resource-group mi-grupo \
  --name mi-mysql-incidentes \
  --admin-user adminsql \
  --admin-password "<password-fuerte>" \
  --sku-name Standard_B1ms
```

Luego usa su cadena de conexión en `DATABASE_URL`.

## Documentación / capturas sugeridas

- Comandos exactos usados (sin credenciales) — ya documentados arriba.
- Captura de los recursos creados en el **portal de Azure**
  (ACR + Container Instance) → `capturas/azure-recursos.png`.
- URL pública de la app funcionando (puedes apagar el recurso después y dejar la
  captura como evidencia para no generar costos).

## Limpieza (para evitar costos)

```bash
az container delete --resource-group mi-grupo --name security-dashboard --yes
az group delete --name mi-grupo --yes --no-wait   # borra TODO el grupo
```
