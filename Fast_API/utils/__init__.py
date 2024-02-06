from Fast_API.Database.database import engine
from Fast_API.Database.models import Base
from Fast_API.settings import Settings
from .logger import loggers
from fastapi import FastAPI
from .api import router


def create_app() -> FastAPI:
    loggers["info"].info("Creating FastAPI app.")
    app = FastAPI()
    app.config = Settings()
    Base.metadata.create_all(bind=engine)
    app.include_router(router)
    loggers["info"].info("FastAPI app created successfully.")
    return app
