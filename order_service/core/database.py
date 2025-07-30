from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from core.config import settings

# Database configuration
DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()