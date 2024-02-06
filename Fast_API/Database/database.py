from sqlalchemy.orm import sessionmaker, scoped_session
from Fast_API.settings import Settings
from sqlalchemy import create_engine
from Fast_API.logger import loggers
from sqlalchemy.orm import Session

setting = Settings()


def create_engine_from_factory():
    return create_engine(
        setting.database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
    )


engine = create_engine_from_factory()


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.engine = engine
            cls._instance.session_maker = sessionmaker(
                autocommit=False, autoflush=False, bind=cls._instance.engine
            )
        return cls._instance

    def get_session(self):
        session = self._instance.session_maker()
        try:
            yield session
        finally:

            session.close()


loggers["info"].info("Database setup completed.")


class GeneralDatabaseAction:

    def add_item(self, item, db_session):
        db_session.add(item)

    def commit_changes(self, db_session):
        db_session.commit()

    def refresh_item(self, item, db_session):
        db_session.refresh(item)
