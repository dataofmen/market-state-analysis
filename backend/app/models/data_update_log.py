from sqlalchemy import Column, Integer, DateTime, String, Text
from sqlalchemy.sql import func
from app.db.base_class import Base


class DataUpdateLog(Base):
    __tablename__ = "data_update_logs"

    id = Column(Integer, primary_key=True, index=True)
    update_type = Column(String, nullable=False)  # 'price', 'indicators', 'market_state'
    status = Column(String, nullable=False)  # 'success', 'failed', 'partial'
    symbols_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
