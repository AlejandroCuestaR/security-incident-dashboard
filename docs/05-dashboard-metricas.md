# 05 — Dashboard de métricas con Chart.js

## Métricas implementadas

Se exponen **3 endpoints de métricas** que devuelven JSON listo para graficar:

| Endpoint | Agrupa por | Gráfica en dashboard |
|----------|-----------|----------------------|
| `GET /incidentes/metricas/severidad` | Severidad | Dona (doughnut) |
| `GET /incidentes/metricas/estado` | Estado | Barras (bar) |
| `GET /incidentes/metricas/mitre` | Técnica MITRE | (disponible vía API) |

Cada endpoint hace un `GROUP BY` en SQL y devuelve un diccionario
`{ categoria: conteo }`. Por ejemplo:

```json
// GET /incidentes/metricas/severidad
{ "baja": 3, "media": 5, "alta": 2, "critica": 4 }
```

## Cómo se grafican (Chart.js)

En `dashboard.html` el navegador consume los endpoints con `fetch` y dibuja las
gráficas. Ejemplo de la dona de severidad:

```javascript
fetch('/incidentes/metricas/severidad')
  .then(res => res.json())
  .then(data => {
    new Chart(document.getElementById('graficaSeveridad'), {
      type: 'doughnut',
      data: {
        labels: Object.keys(data),
        datasets: [{
          data: Object.values(data),
          backgroundColor: ['#6c757d','#ffc107','#fd7e14','#dc3545']
        }]
      },
      options: { plugins: { title: { display: true, text: 'Incidentes por severidad' } } }
    });
  });
```

La segunda gráfica (barras por estado) sigue el mismo patrón contra
`/incidentes/metricas/estado`. Así las gráficas **siempre reflejan datos reales**
de la base de datos, no valores hardcodeados.

## Valor para un equipo SOC

Estas métricas permiten tomar decisiones operativas concretas:

- **Por severidad:** si un alto porcentaje de incidentes son **críticos**, es
  señal de que los controles preventivos están fallando y hay que reforzarlos
  (parches, segmentación, EDR). También ayuda a justificar presupuesto.
- **Por estado:** muchos incidentes **abiertos** o **en progreso** acumulados
  indican un cuello de botella en la respuesta (falta de personal o de
  automatización). Un buen ratio de **cerrados** mide la capacidad de respuesta
  del equipo (relacionado con métricas tipo MTTR).
- **Por técnica MITRE:** si una técnica (p. ej. `T1566` Phishing) se repite,
  conviene priorizar controles específicos para esa técnica (filtrado de correo,
  concientización, MFA).

## Captura sugerida

Carga datos con `python seed.py`, abre `http://localhost:8000/dashboard` y
guarda la captura con las gráficas funcionando como
**`capturas/dashboard.png`**.
