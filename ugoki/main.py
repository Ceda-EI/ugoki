from fastapi import FastAPI

from . import config, models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Serves static directory at /static only in dev mode
if config.DEV_MODE:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(config.STORAGE)),
              name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
