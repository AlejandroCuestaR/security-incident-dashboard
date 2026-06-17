# 08 — BONUS: Integración con Wazuh (Home SOC Lab)

Este endpoint conecta el dashboard (desarrollo Full Stack) con la operación de
seguridad real (SOC), recibiendo alertas de **Wazuh** y registrándolas
automáticamente como incidentes. Demuestra un perfil que une **operación de
seguridad** con **desarrollo**.

## Endpoint

```
POST /incidentes/desde-wazuh
```

Cuerpo (JSON) — subconjunto de una alerta de Wazuh:

```json
{
  "rule_description": "Multiple authentication failures",
  "rule_level": 10,
  "mitre_id": "T1110",
  "agent_name": "web-server-01"
}
```

## Lógica de mapeo

Wazuh asigna a cada regla un **nivel de 0 a 15**. Se traduce a la severidad del
dashboard así:

| `rule_level` (Wazuh) | Severidad del dashboard |
|----------------------|-------------------------|
| 12 – 15 | crítica |
| 8 – 11 | alta |
| 4 – 7 | media |
| 0 – 3 | baja |

El campo `mitre_id` de Wazuh se guarda en `tecnica_mitre`, y la alerta se asigna
a un usuario "de sistema" (el primer usuario registrado).

## Cómo conectarlo con Wazuh

Hay dos enfoques:

1. **Integración por webhook** (recomendado): configura un *integration script*
   en `ossec.conf` que haga `POST` a este endpoint cuando se dispare una alerta
   por encima de cierto nivel.

   ```xml
   <integration>
     <name>custom-dashboard</name>
     <hook_url>http://<host>:8000/incidentes/desde-wazuh</hook_url>
     <level>8</level>
     <alert_format>json</alert_format>
   </integration>
   ```

   El script de integración transforma el JSON de Wazuh al formato esperado por
   el endpoint (`rule_description`, `rule_level`, `mitre_id`, `agent_name`).

2. **Polling de la API de Wazuh**: un job periódico consulta
   `GET /security/events` (Wazuh API) y reenvía las alertas nuevas a este
   endpoint.

## Prueba rápida (sin Wazuh)

Simula una alerta con `curl`:

```bash
curl -X POST http://localhost:8000/incidentes/desde-wazuh \
  -H "Content-Type: application/json" \
  -d '{"rule_description":"Brute force detected","rule_level":12,"mitre_id":"T1110","agent_name":"web-01"}'
```

El incidente aparecerá en el dashboard con severidad **crítica** y técnica
**T1110**.

## Nota de seguridad

Este endpoint no exige JWT (es un webhook entrante). En producción protégelo con
un *secret* compartido en un header, una IP allowlist o mTLS, para que solo tu
instancia de Wazuh pueda publicar alertas.
