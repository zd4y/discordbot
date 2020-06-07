from .config import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(Settings.DATABASE_URL, echo=False)
session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
Base = declarative_base()
Base.query = session.query_property()
