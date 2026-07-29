"""
PostgreSQL setup via SQLAlchemy.
Stores every budget calculation as history so the dashboard can show past trips
and so /optimize-budget can reference the last calculation for a session.
"""
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

# pool_pre_ping avoids stale-connection errors if Postgres restarts
# Attempt to connect to PostgreSQL. If it fails, fall back to SQLite!
try:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    # Quick connection test
    with engine.connect() as conn:
        pass
    print("[database] Connected to PostgreSQL successfully.")
except Exception as e:
    db_path = settings.DATASETS_DIR.parent / "budget_history.db"
    print(f"[database] PostgreSQL connection failed: {e}. Falling back to SQLite at: {db_path}")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False} if "sqlite" in f"sqlite:///{db_path}" else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class BudgetRequest(Base):
    __tablename__ = "budget_requests"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, index=True)
    days = Column(Integer)
    travelers = Column(Integer)
    budget = Column(Float)
    travel_style = Column(String)

    total_estimated_cost = Column(Float)
    remaining = Column(Float)
    breakdown = Column(JSON)
    daily_breakdown = Column(JSON)
    recommendations = Column(JSON)
    ai_recommendation_text = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create tables if they don't exist. Called on app startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
