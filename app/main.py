from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from .routers import incidentes, usuarios, auth as auth_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Security Incident Dashboard")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(incidentes.router)
app.include_router(usuarios.router)
app.include_router(auth_router.router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    incidentes_list = db.query(models.Incidente).all()
    return templates.TemplateResponse(
        request, "dashboard.html", {"incidentes": incidentes_list}
    )


@app.get("/incidentes-vista")
def incidentes_vista(request: Request, db: Session = Depends(get_db)):
    incidentes_list = db.query(models.Incidente).all()
    return templates.TemplateResponse(
        request, "incidentes.html", {"incidentes": incidentes_list}
    )
