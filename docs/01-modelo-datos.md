# 01 — Modelo de datos

El modelo se compone de **3 tablas**: `usuarios`, `incidentes` y `logs_actividad`.

## Diagrama Entidad-Relación

```
┌─────────────────────────┐
│        usuarios         │
├─────────────────────────┤
│ PK  id            INT   │
│     nombre        STR   │
│     email         STR U │◀──────┐
│     hashed_password STR │       │
│     rol           STR   │       │ 1
└─────────────────────────┘       │
            │ 1                    │
            │                      │
            │ N                    │ N
┌─────────────────────────┐       │
│       incidentes        │       │
├─────────────────────────┤       │
│ PK  id            INT   │       │
│     titulo        STR   │       │
│     descripcion   STR   │       │
│     severidad     ENUM  │       │
│     estado        ENUM  │       │
│     tecnica_mitre STR   │       │
│ FK  analista_id   INT   │───────┘
│     fecha_creacion DT   │
│     fecha_actualizacion DT │
└─────────────────────────┘
            │ 1
            │
            │ N
┌─────────────────────────┐
│     logs_actividad      │
├─────────────────────────┤
│ PK  id            INT   │
│ FK  incidente_id  INT   │
│ FK  usuario_id    INT   │
│     accion        STR   │
│     fecha         DT    │
└─────────────────────────┘
```

> Puedes regenerar este diagrama de forma visual en [dbdiagram.io](https://dbdiagram.io)
> con el siguiente DBML y exportar la imagen a `capturas/modelo-er.png`:

```dbml
Table usuarios {
  id int [pk, increment]
  nombre varchar(100)
  email varchar(100) [unique]
  hashed_password varchar(255)
  rol varchar(20)
}

Table incidentes {
  id int [pk, increment]
  titulo varchar(200)
  descripcion varchar(1000)
  severidad varchar [note: 'enum: baja/media/alta/critica']
  estado varchar [note: 'enum: abierto/en_progreso/cerrado']
  tecnica_mitre varchar(20)
  analista_id int [ref: > usuarios.id]
  fecha_creacion datetime
  fecha_actualizacion datetime
}

Table logs_actividad {
  id int [pk, increment]
  incidente_id int [ref: > incidentes.id]
  usuario_id int [ref: > usuarios.id]
  accion varchar(255)
  fecha datetime
}
```

## Descripción de tablas y relaciones

### `usuarios`
Analistas del SOC que usan el sistema. El `email` es único (sirve como
identificador de login). La contraseña **nunca** se guarda en claro: se almacena
su hash bcrypt en `hashed_password`.

### `incidentes`
Entidad central. Cada incidente pertenece a **un** analista (`analista_id`),
mientras que un analista puede tener **muchos** incidentes →
**relación 1 a N** (`Usuario.incidentes` ↔ `Incidente.analista`).

### `logs_actividad`
Bitácora de auditoría: registra acciones realizadas sobre los incidentes
(quién hizo qué y cuándo). Relacionada tanto con `incidentes` como con
`usuarios`. Pensada como base para trazabilidad/auditoría.

## Relaciones (resumen)

| Relación | Cardinalidad | Implementación |
|----------|--------------|----------------|
| Usuario → Incidente | 1 : N | `analista_id` FK + `relationship(back_populates)` |
| Incidente → LogActividad | 1 : N | `incidente_id` FK |
| Usuario → LogActividad | 1 : N | `usuario_id` FK |

## ¿Por qué `Enum` para severidad y estado?

Se usó el tipo `Enum` de SQLAlchemy (respaldado por `enum.Enum` de Python) en
lugar de un `String` libre por tres razones:

1. **Consistencia de datos:** solo se aceptan valores válidos
   (`baja/media/alta/critica`, `abierto/en_progreso/cerrado`). Es imposible
   guardar "Critico", "CRÍTICA" o un typo como "abiero".
2. **Validación en dos capas:** Pydantic valida la entrada en la API y la base
   de datos restringe el dominio a nivel de columna.
3. **Mantenibilidad:** los valores válidos viven en un único lugar
   (`app/models.py`), lo que facilita agregar o cambiar estados en el futuro.

Esto evita el clásico problema de datos sucios que dificultan las métricas
(p. ej. agrupar por severidad y obtener "alta" y "Alta" como categorías
distintas).
