"Main app"
import hashlib
import random
import secrets
from typing import List

import aiofiles
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
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
async def list_categories(db: Session = Depends(get_db)):
    "Lists all categories and count"
    all_categories = db.query(m.Category).all()
    return all_categories


@app.post("/category/{name}", dependencies=[Depends(require_auth)],
          response_model=s.Success)
async def create_category(name, db: Session = Depends(get_db)):
    "Adds a category"

    try:
        db.add(m.Category(name=name))
        db.commit()
        return {"success": True}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@app.get("/category/{name}/gif", response_model=s.Gif)
async def get_gif(name, db: Session = Depends(get_db)):
    "Returns a gif"

    gifs = db.query(m.Gif).filter_by(approved=True, category_name=name).all()

    if not gifs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return random.choice(gifs)


@app.get("/suggestions", response_model=List[s.Suggestion],
         dependencies=[Depends(require_auth)])
async def list_suggestions(db: Session = Depends(get_db)):
    "Returns the list of suggestions"
    return db.query(m.Gif).filter_by(approved=False).limit(15).all()


@app.post("/suggestion/{sug_id}", dependencies=[Depends(require_auth)],
          response_model=s.Success)
async def approve_suggestion(sug_id, db: Session = Depends(get_db)):
    "Approves the suggestion"
    db.query(m.Gif).filter_by(id=sug_id, approved=False).update(
        {m.Gif.approved: True})
    db.commit()
    return {"success": True}


@app.delete("/suggestion/{sug_id}", dependencies=[Depends(require_auth)],
            response_model=s.Success)
async def reject_suggestion(sug_id, db: Session = Depends(get_db)):
    "Rejects the suggestion"
    try:
        gif = db.query(m.Gif).filter_by(id=sug_id, approved=False).one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(gif)
    db.commit()
    gif_file = config.STORAGE / (sug_id + ".gif")
    if not gif_file.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    gif_file.unlink(missing_ok=True)

    return {"success": True}


@app.delete("/gif/{gif_id}", dependencies=[Depends(require_auth)],
            response_model=s.Success)
async def delete_gif(gif_id):
    gif = config.STORAGE / (gif_id + ".gif")
    if not gif.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    gif.unlink(missing_ok=True)
    return {"success": True}


@app.post("/new_suggestion/{category}", response_model=s.Suggestion)
async def create_suggestion(category: str, file: UploadFile = File(...),
                            db: Session = Depends(get_db)):
    # Ensure that the category exists
    if db.query(m.Category).get(category) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Ensure that the file is a gif
    if file.content_type != "image/gif":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    contents = await file.read()
    gif_hash = hashlib.sha256(contents).hexdigest()

    # Ensure it doesn't already exist
    if db.query(m.Gif).get(gif_hash) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    gif = m.Gif(id=gif_hash, category_name=category, approved=False)
    db.add(gif)
    db.commit()

    filename = config.STORAGE / (gif_hash + ".gif")
    async with aiofiles.open(filename, "wb") as gif_file:
        await gif_file.write(contents)

    return gif
