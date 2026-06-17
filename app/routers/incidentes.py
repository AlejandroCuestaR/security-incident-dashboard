from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/incidentes", tags=["incidentes"])


# --- BONUS: integración con Wazuh (ver docs/08-integracion-wazuh.md) ---------
class AlertaWazuh(BaseModel):
    """Subconjunto del JSON de una alerta de Wazuh que nos interesa."""
    rule_description: str
    rule_level: int
    mitre_id: Optional[str] = None
    agent_name: Optional[str] = None


@router.post("/", response_model=schemas.IncidenteOut)
def crear_incidente(
    incidente: schemas.IncidenteCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    nuevo = models.Incidente(**incidente.dict(), analista_id=current_user.id)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get("/", response_model=list[schemas.IncidenteOut])
def listar_incidentes(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    return db.query(models.Incidente).all()


# ---------------------------------------------------------------------------
# Endpoints de métricas (deben ir ANTES de /{incidente_id} para que FastAPI
# no interprete "metricas" como un id de incidente).
# ---------------------------------------------------------------------------
@router.get("/metricas/severidad")
def metricas_por_severidad(db: Session = Depends(get_db)):
    resultados = (
        db.query(models.Incidente.severidad, func.count(models.Incidente.id))
        .group_by(models.Incidente.severidad)
        .all()
    )
    return {sev.value: count for sev, count in resultados}


@router.get("/metricas/estado")
def metricas_por_estado(db: Session = Depends(get_db)):
    resultados = (
        db.query(models.Incidente.estado, func.count(models.Incidente.id))
        .group_by(models.Incidente.estado)
        .all()
    )
    return {estado.value: count for estado, count in resultados}


@router.get("/metricas/mitre")
def metricas_por_mitre(db: Session = Depends(get_db)):
    resultados = (
        db.query(models.Incidente.tecnica_mitre, func.count(models.Incidente.id))
        .group_by(models.Incidente.tecnica_mitre)
        .all()
    )
    return {(mitre or "sin_clasificar"): count for mitre, count in resultados}


@router.post("/desde-wazuh", response_model=schemas.IncidenteOut)
def crear_desde_wazuh(alerta: AlertaWazuh, db: Session = Depends(get_db)):
    """
    BONUS — Recibe una alerta de Wazuh (webhook) y la inserta como incidente.
    Mapea el nivel de la regla de Wazuh (0-15) a la severidad del dashboard.
    Pensado para integrarse con el Proyecto 1 (Home SOC Lab).
    """
    if alerta.rule_level >= 12:
        severidad = models.SeveridadEnum.critica
    elif alerta.rule_level >= 8:
        severidad = models.SeveridadEnum.alta
    elif alerta.rule_level >= 4:
        severidad = models.SeveridadEnum.media
    else:
        severidad = models.SeveridadEnum.baja

    # Se asigna al primer usuario como analista por defecto (cuenta de sistema).
    analista = db.query(models.Usuario).order_by(models.Usuario.id).first()
    if not analista:
        raise HTTPException(
            status_code=400,
            detail="No hay usuarios registrados para asignar la alerta",
        )

    descripcion = alerta.rule_description
    if alerta.agent_name:
        descripcion = f"[{alerta.agent_name}] {descripcion}"

    nuevo = models.Incidente(
        titulo=f"[Wazuh] {alerta.rule_description[:180]}",
        descripcion=descripcion[:1000],
        severidad=severidad,
        tecnica_mitre=alerta.mitre_id,
        analista_id=analista.id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get("/{incidente_id}", response_model=schemas.IncidenteOut)
def obtener_incidente(
    incidente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    incidente = (
        db.query(models.Incidente)
        .filter(models.Incidente.id == incidente_id)
        .first()
    )
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incidente


@router.patch("/{incidente_id}", response_model=schemas.IncidenteOut)
def actualizar_incidente(
    incidente_id: int,
    datos: schemas.IncidenteUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    incidente = (
        db.query(models.Incidente)
        .filter(models.Incidente.id == incidente_id)
        .first()
    )
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(incidente, key, value)
    db.commit()
    db.refresh(incidente)
    return incidente


@router.delete("/{incidente_id}")
def eliminar_incidente(
    incidente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    incidente = (
        db.query(models.Incidente)
        .filter(models.Incidente.id == incidente_id)
        .first()
    )
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    db.delete(incidente)
    db.commit()
    return {"mensaje": "Incidente eliminado"}
