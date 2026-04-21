"""Database models and configuration for metrics storage."""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./metrics.db")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class EvaluationRun(Base):
    """Evaluation run record - one per comparison query."""
    __tablename__ = "evaluation_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    query = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    document_name = Column(String, nullable=True)
    
    # Relationships
    responses = relationship("ModelResponseDB", back_populates="run", cascade="all, delete-orphan")


class ModelResponseDB(Base):
    """Model response record - one per model per run."""
    __tablename__ = "model_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("evaluation_runs.id"), index=True)
    model_name = Column(String, index=True)
    response_text = Column(Text)
    response_time = Column(Float)
    token_count = Column(Integer)
    cost_estimate = Column(Float)
    
    # Relationships
    run = relationship("EvaluationRun", back_populates="responses")
    quality = relationship("QualityMetricDB", back_populates="response", uselist=False, cascade="all, delete-orphan")


class QualityMetricDB(Base):
    """Quality metrics for a model response."""
    __tablename__ = "quality_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("model_responses.id"), index=True)
    semantic_similarity = Column(Float)
    context_relevance = Column(Float)
    citation_quality = Column(Float)
    completeness_score = Column(Float)
    
    # Relationships
    response = relationship("ModelResponseDB", back_populates="quality")


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Get database session.
    Use as dependency in FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
