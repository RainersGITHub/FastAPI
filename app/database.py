from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

DATABASE_TYPE = settings.DATABASE_TYPE
USERNAME = settings.USERNAME
PASSWORD = settings.PASSWORD
HOST = settings.HOST
PORT = settings.PORT
DATABASE_NAME = settings.DATABASE_NAME
ENCODING = settings.ENCODING
SQLALCHEMY_DATABASE_URL = f"{DATABASE_TYPE}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"

engine = create_engine(f"{SQLALCHEMY_DATABASE_URL}", client_encoding=f"{ENCODING}", echo=True)

SessionLocal = sessionmaker(engine, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
