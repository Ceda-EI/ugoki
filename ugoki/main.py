"Main app"
import random
import secrets
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm.session import Session

from . import config, models as m, schemas as s
from .database import SessionLocal, engine

m.Base.metadata.create_all(bind=engine)
app = FastAPI()
security = HTTPBasic()

# Serves static directory at /static only in dev mode
if config.DEV_MODE:
    from fastapi.staticfiles import StaticFiles  # pylint: disable=C0412
    app.mount("/static", StaticFiles(directory=str(config.STORAGE)),
              name="static")


def require_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Adding this to dependencies of a route ensures that the route is only
    called by authenticated user
    """

    c_un = secrets.compare_digest(credentials.username, config.AUTH_USER)
    c_pw = secrets.compare_digest(credentials.password, config.AUTH_PASSWORD)
    if not (c_un and c_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def get_db():
    "Returns the database"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/categories", response_model=List[s.Category])
async def categories(db: Session = Depends(get_db)):
    "Lists all categories and count"
    all_categories = db.query(m.Category).all()
    return all_categories


@app.post("/category/{name}", dependencies=[Depends(require_auth)])
async def category(name, db: Session = Depends(get_db)):
    "Adds a category"

    try:
        db.add(m.Category(name=name))
        db.commit()
        return {"success": True}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@app.get("/category/{name}/gif", response_model=s.Gif)
async def gif(name, db: Session = Depends(get_db)):
    "Returns a gif"

    gifs = db.query(m.Gif).filter_by(approved=True, category_name=name).all()

    if not gifs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return random.choice(gifs)


@app.get("/suggestions", response_model=List[s.Suggestion],
         dependencies=[Depends(require_auth)])
async def suggestions(db: Session = Depends(get_db)):
    "Returns the list of suggestions"
    return db.query(m.Gif).filter_by(approved=False).all()


@app.post("/suggestion/{sug_id}", dependencies=[Depends(require_auth)])
async def approve(sug_id, db: Session = Depends(get_db)):
    "Approves the suggestion"
    db.query(m.Gif).filter_by(id=sug_id, approved=False).update(
        {m.Gif.approved: True})
    db.commit()
    return {"success": True}


@app.delete("/suggestion/{sug_id}", dependencies=[Depends(require_auth)])
async def reject(sug_id, db: Session = Depends(get_db)):
    "Rejects the suggestion"
    try:
        gif = db.query(m.Gif).filter_by(id=sug_id, approved=False).one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(gif)
    db.commit()
    gif_file = config.STORAGE / sug_id + ".gif"
    if not gif_file.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    gif_file.unlink()

    return {"success": True}


@app.delete("/gif/{gif_id}", dependencies=[Depends(require_auth)])
async def delete_gif(gif_id):
    gif = config.STORAGE / gif_id + ".gif"
    if not gif.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    gif.unlink()
    return {"success": True}
