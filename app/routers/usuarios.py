from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=schemas.UsuarioOut)
def usuario_actual(current_user: models.Usuario = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado (a partir del token JWT)."""
    return current_user


@router.get("/", response_model=list[schemas.UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Lista todos los usuarios. Requiere autenticación."""
    return db.query(models.Usuario).all()
