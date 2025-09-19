from sqlalchemy import Column, Integer, String
from .base import Base


class DomesticFutureoptionMaster(Base):
    """국내선물옵션 마스터"""
    __tablename__ = 'domestic_futureoption_master'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), index=True)  # 종목명
    code = Column(String(50), index=True)  # 종목코드
    ex = Column(String(30), index=True)    # 거래소 코드
