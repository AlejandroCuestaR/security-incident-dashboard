from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["autenticacion"])


@router.post("/registro", response_model=schemas.UsuarioOut)
def registrar(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existente = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == usuario.email)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    nuevo = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        hashed_password=auth.hashear_password(usuario.password),
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == form_data.username)
        .first()
    )
    if not usuario or not auth.verificar_password(
        form_data.password, usuario.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = auth.crear_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}
