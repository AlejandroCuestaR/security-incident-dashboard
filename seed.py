"""
Carga datos de ejemplo en la base de datos para probar el dashboard.

Uso:
    python seed.py

Crea un usuario analista (si no existe) y varios incidentes de muestra con
distintas severidades, estados y técnicas MITRE.
"""
from app.database import SessionLocal, engine
from app import models
from app.auth import hashear_password

# Asegura que las tablas existan
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# --- Usuario analista de ejemplo -------------------------------------------
EMAIL = "analista@soc.local"
analista = db.query(models.Usuario).filter(models.Usuario.email == EMAIL).first()
if not analista:
    analista = models.Usuario(
        nombre="Analista SOC",
        email=EMAIL,
        hashed_password=hashear_password("Cambiame123"),
        rol="analista",
    )
    db.add(analista)
    db.commit()
    db.refresh(analista)
    print(f"Usuario creado: {EMAIL} / Cambiame123")
else:
    print(f"Usuario ya existe: {EMAIL}")

# --- Incidentes de ejemplo --------------------------------------------------
ejemplos = [
    ("Phishing dirigido a finanzas", "Correo con enlace malicioso a usuarios de finanzas.",
     models.SeveridadEnum.alta, models.EstadoEnum.en_progreso, "T1566"),
    ("Fuerza bruta en RDP", "Multiples intentos de login fallidos contra el servidor RDP.",
     models.SeveridadEnum.critica, models.EstadoEnum.abierto, "T1110"),
    ("Malware detectado en endpoint", "EDR aisló un binario sospechoso en EQ-204.",
     models.SeveridadEnum.critica, models.EstadoEnum.cerrado, "T1059"),
    ("Escaneo de puertos externo", "Escaneo desde IP externa hacia el perímetro.",
     models.SeveridadEnum.media, models.EstadoEnum.cerrado, "T1046"),
    ("Cuenta creada fuera de horario", "Alta de usuario administrador a las 03:00.",
     models.SeveridadEnum.alta, models.EstadoEnum.abierto, "T1136"),
    ("Tráfico a dominio sospechoso", "Conexión a dominio recién registrado (posible C2).",
     models.SeveridadEnum.media, models.EstadoEnum.en_progreso, "T1071"),
    ("Aviso informativo de actualización", "Pendiente aplicar parche en servidor de pruebas.",
     models.SeveridadEnum.baja, models.EstadoEnum.abierto, None),
]

creados = 0
for titulo, desc, sev, estado, mitre in ejemplos:
    existe = db.query(models.Incidente).filter(models.Incidente.titulo == titulo).first()
    if existe:
        continue
    db.add(models.Incidente(
        titulo=titulo, descripcion=desc, severidad=sev,
        estado=estado, tecnica_mitre=mitre, analista_id=analista.id,
    ))
    creados += 1

db.commit()
db.close()
print(f"Incidentes de ejemplo creados: {creados}")
print("Listo. Abre http://localhost:8000/dashboard")
