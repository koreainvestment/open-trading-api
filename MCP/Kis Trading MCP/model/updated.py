from sqlalchemy import Column, Integer, String, DateTime
from .base import Base


class Updated(Base):
    """마스터파일 업데이트 상태 추적 테이블"""
    __tablename__ = 'updated'
    
    id = Column(Integer, primary_key=True)
    tool_name = Column(String(50), nullable=False, unique=True, index=True)  # 툴명 (예: domestic_stock, overseas_stock)
    updated_at = Column(DateTime, nullable=False)  # 마지막 업데이트 시간
    
    def __repr__(self):
        return f"<Updated(tool_name='{self.tool_name}', updated_at='{self.updated_at}')>"

