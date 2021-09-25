from fastapi import FastAPI

from . import config

app = FastAPI()

if config.DEV_MODE:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=config.STORAGE), name="static")
