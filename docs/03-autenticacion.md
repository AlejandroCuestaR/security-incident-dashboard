# 03 — Autenticación con JWT

## Flujo completo

```
1) REGISTRO
   Cliente ──POST /auth/registro {nombre, email, password}──▶ FastAPI
   FastAPI: hashea password con bcrypt y guarda el usuario en MySQL
   FastAPI ──201 {id, nombre, email, rol}──▶ Cliente   (nunca devuelve el hash)

2) LOGIN
   Cliente ──POST /auth/login (form: username=email, password)──▶ FastAPI
   FastAPI: busca usuario por email y verifica el hash bcrypt
   FastAPI: firma un JWT  { sub: email, exp: ahora + 60 min }  con SECRET_KEY
   FastAPI ──200 {access_token, token_type: "bearer"}──▶ Cliente

3) USO DEL TOKEN (endpoint protegido)
   Cliente ──GET /incidentes/  (Header: Authorization: Bearer <token>)──▶ FastAPI
   FastAPI (get_current_user): decodifica y valida el JWT con SECRET_KEY
                               extrae 'sub' (email) y carga el usuario de MySQL
   FastAPI ──200 [incidentes...]──▶ Cliente
   (si el token falta, expiró o es inválido → 401 Unauthorized)
```

## Diagrama de secuencia (login + acceso protegido)

```
Cliente            FastAPI(/auth)        auth.py            MySQL
  │  login            │                    │                  │
  │──────────────────▶│  verificar_password│                  │
  │                   │───────────────────▶│   query usuario  │
  │                   │                    │─────────────────▶│
  │                   │                    │◀─────────────────│
  │                   │   crear_token()    │                  │
  │                   │───────────────────▶│                  │
  │   {access_token}  │◀───────────────────│                  │
  │◀──────────────────│                    │                  │
  │                                                            │
  │  GET /incidentes  (Authorization: Bearer <token>)         │
  │──────────────────▶│  get_current_user  │                  │
  │                   │───────────────────▶│ jwt.decode()     │
  │                   │                    │   query usuario  │
  │                   │                    │─────────────────▶│
  │   [incidentes]    │◀───────────────────│◀─────────────────│
  │◀──────────────────│                    │                  │
```

## Componentes

| Función (`app/auth.py`) | Rol |
|-------------------------|-----|
| `hashear_password` | Genera el hash bcrypt al registrar |
| `verificar_password` | Compara password en claro vs hash en login |
| `crear_token` | Firma el JWT con `SECRET_KEY` y expiración |
| `get_current_user` | Dependencia que protege endpoints: decodifica el token y carga el usuario |

El login usa `OAuth2PasswordRequestForm`, por lo que el cliente envía
`username` (el email) y `password` como **datos de formulario**
(`application/x-www-form-urlencoded`), no como JSON. El token se entrega en el
header `Authorization: Bearer <token>` en cada petición protegida.

## Buenas prácticas aplicadas

- **Passwords hasheados con bcrypt** (`passlib`): nunca se almacena ni se
  devuelve la contraseña en claro. Bcrypt incluye *salt* automático y es lento
  a propósito (resistente a fuerza bruta).
- **Tokens con expiración** (`exp`): por defecto 60 minutos
  (`ACCESS_TOKEN_EXPIRE_MINUTES`). Un token robado deja de servir pronto.
- **`SECRET_KEY` fuera del código:** se lee de variables de entorno (`.env`),
  que está en `.gitignore`. El repositorio solo incluye `.env.example` sin
  secretos reales.
- **Respuestas con `response_model`:** `UsuarioOut` excluye `hashed_password` de
  toda respuesta de la API.
- **Errores genéricos en login:** se responde "Credenciales incorrectas" sin
  revelar si el fallo fue por email inexistente o password incorrecto.

## Recomendaciones para producción (más allá del MVP)

- Servir siempre sobre **HTTPS** (los Bearer tokens viajan en texto plano del
  lado del transporte).
- Considerar **refresh tokens** y/o cookies `httpOnly` en vez de `localStorage`.
- Rotar `SECRET_KEY` y usar una clave larga y aleatoria
  (`openssl rand -hex 32`).
