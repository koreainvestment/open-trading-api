"""데이터 변환기 - KIS DataFrame을 Lean CSV 포맷으로 변환

KIS OpenAPI 데이터를 Lean이 읽을 수 있는 CSV 포맷으로 변환.
"""

import logging
from pathlib import Path
from typing import Dict, List, TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ..models import Bar

logger = logging.getLogger(__name__)


class DataConverter:
    """KIS DataFrame → Lean CSV 변환기"""
    
    @classmethod
    def export(
        cls,
        data_dict: Dict[str, pd.DataFrame],
        output_dir: str,
        market_type: str = "krx",
    ) -> Dict[str, Path]:
        """데이터를 Lean CSV 포맷으로 내보내기
        
        Args:
            data_dict: {symbol: DataFrame} 형태의 데이터
            output_dir: 출력 디렉토리 경로
            market_type: "krx" (국내) 또는 "us" (해외)
        
        Returns:
            {symbol: Path} 형태의 생성된 파일 경로
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        exported = {}
        
        for symbol, df in data_dict.items():
            try:
                csv_path = cls._export_symbol(symbol, df, output_path, market_type)
                exported[symbol] = csv_path
                logger.debug(f"  - {symbol}: {csv_path}")
            except Exception as e:
                logger.error(f"  - {symbol} 변환 실패: {e}")
        
        return exported
    
    @classmethod
    def _export_symbol(
        cls,
        symbol: str,
        df: pd.DataFrame,
        output_dir: Path,
        market_type: str = "krx",
    ) -> Path:
        """단일 종목 데이터 변환
        
        Args:
            symbol: 종목 코드
            df: 데이터프레임
            output_dir: 출력 디렉토리
            market_type: "krx" (국내) 또는 "us" (해외)
        """
        # 컬럼 정규화
        df_out = df.copy()
        
        # 날짜 컬럼 처리
        if 'date' in df_out.columns:
            df_out['date'] = pd.to_datetime(df_out['date'])
        elif df_out.index.name == 'date' or isinstance(df_out.index, pd.DatetimeIndex):
            df_out = df_out.reset_index()
            df_out.columns.values[0] = 'date'
            df_out['date'] = pd.to_datetime(df_out['date'])
        
        # 필수 컬럼 확인
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df_out.columns:
                raise ValueError(f"필수 컬럼 없음: {col}")
        
        # Lean 포맷으로 변환 (YYYYMMDD,open,high,low,close,volume)
        df_out['date_str'] = df_out['date'].dt.strftime('%Y%m%d')
        
        # 중복 제거 (날짜 기준)
        df_out = df_out.drop_duplicates(subset=['date_str'], keep='first')
        df_out = df_out.sort_values('date_str')
        
        # 가격 포맷: KRX는 정수(원), US는 소수점 2자리(달러)
        if market_type == "krx":
            # 한국 주식: 원 단위 (정수)
            for col in required_cols:
                df_out[col] = df_out[col].astype(float).round(0).astype(int)
        else:
            # 미국 주식: 달러 단위 (소수점 2자리)
            for col in ['open', 'high', 'low', 'close']:
                df_out[col] = df_out[col].astype(float).round(2)
            df_out['volume'] = df_out['volume'].astype(int)
        
        # CSV 출력 (헤더 없음)
        csv_path = output_dir / f"{symbol.lower()}.csv"
        
        df_out[['date_str', 'open', 'high', 'low', 'close', 'volume']].to_csv(
            csv_path,
            index=False,
            header=False,
        )
        
        return csv_path
    
    @classmethod
    def get_date_range(cls, data_dict: Dict[str, pd.DataFrame]) -> tuple:
        """데이터의 공통 날짜 범위 계산"""
        if not data_dict:
            return None, None
        
        min_date = None
        max_date = None
        
        for df in data_dict.values():
            if df.empty:
                continue
            
            if isinstance(df.index, pd.DatetimeIndex):
                dates = df.index
            elif 'date' in df.columns:
                dates = pd.to_datetime(df['date'])
            else:
                continue
            
            df_min = dates.min()
            df_max = dates.max()
            
            if min_date is None or df_min > min_date:
                min_date = df_min
            if max_date is None or df_max < max_date:
                max_date = df_max
        
        return min_date, max_date
    
    @classmethod
    def bars_to_lean_csv(
        cls,
        bars: List["Bar"],
        symbol: str,
        output_dir: Path,
        market_type: str = "krx",
    ) -> Path:
        """Bar 리스트를 Lean CSV로 변환
        
        Args:
            bars: Bar 객체 리스트
            symbol: 종목 코드
            output_dir: 출력 디렉토리
            market_type: "krx" 또는 "us"
        
        Returns:
            생성된 CSV 파일 경로
        """
        if not bars:
            raise ValueError("빈 bars 리스트")
        
        # Bar → DataFrame
        data = []
        for bar in bars:
            data.append({
                'date': bar.time,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume,
            })
        
        df = pd.DataFrame(data)
        
        # output_dir이 str이면 Path로 변환
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 변환 실행
        return cls._export_symbol(symbol, df, output_path, market_type)