from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./transactions.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    source_account = Column(String, nullable=False)
    destination_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, default="PROCESSING")  # PROCESSING, PROCESSED, FAILED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)
    webhook_received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processing_started_at = Column(DateTime, nullable=True)
    is_processing = Column(Boolean, default=False)
    error_message = Column(String, nullable=True)

    __table_args__ = (
        Index('idx_transaction_id_status', 'transaction_id', 'status'),
        Index('idx_status', 'status'),
    )


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
