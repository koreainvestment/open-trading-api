from sqlalchemy import Column, Integer, String
from .base import Base


class AuthMaster(Base):
    """인증 마스터"""
    __tablename__ = 'auth_master'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), index=True)  # 종목명
    code = Column(String(50), index=True)  # 종목코드
