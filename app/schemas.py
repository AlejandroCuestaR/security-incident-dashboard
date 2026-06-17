from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from .models import SeveridadEnum, EstadoEnum


class IncidenteBase(BaseModel):
    titulo: str
    descripcion: str
    severidad: SeveridadEnum
    tecnica_mitre: Optional[str] = None


class IncidenteCreate(IncidenteBase):
    pass


class IncidenteUpdate(BaseModel):
    estado: Optional[EstadoEnum] = None
    severidad: Optional[SeveridadEnum] = None


class IncidenteOut(IncidenteBase):
    id: int
    estado: EstadoEnum
    analista_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str

    class Config:
        from_attributes = True
