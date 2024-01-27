from .settings import Settings
from .database import engine
from fastapi import FastAPI
from .models import Base
from .api import router
from .logger import loggers


def create_app() -> FastAPI:
    loggers["info"].info("Creating FastAPI app.")
    app = FastAPI()
    app.config = Settings()
    Base.metadata.create_all(bind=engine)
    app.include_router(router)
    loggers["info"].info("FastAPI app created successfully.")
    return app
