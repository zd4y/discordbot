from .config import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(Settings.DATABASE_URL, echo=False)
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)
Base = declarative_base()
Base.query = session.query_property()
