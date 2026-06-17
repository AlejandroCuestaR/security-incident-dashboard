from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class SeveridadEnum(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"


class EstadoEnum(str, enum.Enum):
    abierto = "abierto"
    en_progreso = "en_progreso"
    cerrado = "cerrado"


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    rol = Column(String(20), default="analista")
    incidentes = relationship("Incidente", back_populates="analista")


class Incidente(Base):
    __tablename__ = "incidentes"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200))
    descripcion = Column(String(1000))
    severidad = Column(Enum(SeveridadEnum))
    estado = Column(Enum(EstadoEnum), default=EstadoEnum.abierto)
    tecnica_mitre = Column(String(20), nullable=True)
    analista_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    analista = relationship("Usuario", back_populates="incidentes")


class LogActividad(Base):
    __tablename__ = "logs_actividad"
    id = Column(Integer, primary_key=True, index=True)
    incidente_id = Column(Integer, ForeignKey("incidentes.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    accion = Column(String(255))
    fecha = Column(DateTime, server_default=func.now())
