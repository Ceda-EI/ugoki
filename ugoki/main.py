import secrets
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from . import config, models as m, schemas as s
from .database import SessionLocal, engine

m.Base.metadata.create_all(bind=engine)
app = FastAPI()
security = HTTPBasic()

# Serves static directory at /static only in dev mode
if config.DEV_MODE:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(config.STORAGE)),
              name="static")


def require_auth(credentials: HTTPBasicCredentials = Depends(security)):
    c_un = secrets.compare_digest(credentials.username, config.AUTH_USER)
    c_pw = secrets.compare_digest(credentials.password, config.AUTH_PASSWORD)
    if not (c_un and c_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/categories", response_model=List[s.Category])
async def categories(db: Session = Depends(get_db)):
    all_categories = db.query(m.Category).all()
    return all_categories


@app.post("/category/{name}", status_code=200,
          dependencies=[Depends(require_auth)])
async def category(name, response: Response, db: Session = Depends(get_db)):
    try:
        db.add(m.Category(name=name))
        db.commit()
        return {"success": True}
    except IntegrityError:
        response.status_code = status.HTTP_409_CONFLICT
        return {"success": False}
