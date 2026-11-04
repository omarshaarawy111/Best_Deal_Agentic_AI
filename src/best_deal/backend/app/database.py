"""
Database configuration and session management for the Best Deal project.

Description:
    This module configures the SQLite engine, exposes the SQLAlchemy base
    class, and provides request-scoped database sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# In case of SQLite
SQLALCHEMY_DATABASE_URL = 'sqlite:///./best_deal.db'
# In case of PostgreSQL
# SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

# In case of SQLite or PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite")
    else {}
)
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Provide a database session for a request.

    Yields:
        An active SQLAlchemy session that is closed after request handling.
    """
    db = SessionLocal()
    try:
      yield db
    finally:
      db.close()
