from .base import Base
from .updated import Updated

# 툴별 마스터 모델들
from .domestic_stock import DomesticStockMaster
from .overseas_stock import OverseasStockMaster
from .domestic_futureoption import DomesticFutureoptionMaster
from .overseas_futureoption import OverseasFutureoptionMaster
from .domestic_bond import DomesticBondMaster
from .etfetn import EtfetnMaster
from .elw import ElwMaster
from .auth import AuthMaster


# 모든 모델들을 리스트로 제공
ALL_MODELS = [
    # 툴별 마스터 모델들
    DomesticStockMaster,
    OverseasStockMaster,
    DomesticFutureoptionMaster,
    OverseasFutureoptionMaster,
    DomesticBondMaster,
    EtfetnMaster,
    ElwMaster,
    AuthMaster,
    
    # 업데이트 상태 추적
    Updated
]
