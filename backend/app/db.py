from sqlalchemy import create_engine, text
import pandas as pd
import os
from sqlalchemy.orm import declarative_base,sessionmaker
from .core.config import settings




engine = create_engine(settings.DATABASE_URL)
Base=declarative_base()
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
