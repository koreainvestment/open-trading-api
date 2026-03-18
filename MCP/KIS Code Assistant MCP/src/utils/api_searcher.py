import pandas as pd
from typing import Optional, Dict, Any, List

class APISearcher:
    """API 검색 클래스 - 성능 최적화 버전"""
    
    # 실제 사용되는 정확 매칭 필드만
    EXACT_MATCH_FIELDS = {'subcategory', 'category'}
    MAX_RESULTS = 10
    DESCRIPTION_LENGTH = 100
    
    def __init__(self, filepath: str = "data.csv"):
        self._data = None
        self.load_data(filepath)
    
    def load_data(self, filepath: str = "data.csv") -> str:
        """CSV 데이터 로드 (에러 처리 강화)"""
        try:
            self._data = pd.read_csv(filepath)
            return f"Loaded {len(self._data)} APIs"
        except FileNotFoundError:
            return f"❌ Data file not found: {filepath}"
        except Exception as e:
            return f"❌ Error loading data: {e}"
    
    def search(self, **kwargs) -> dict:
        """통합 API 검색 (성능 최적화)"""
        if self._data is None:
            return {
                "status": "error",
                "message": "Data not loaded",
                "total_count": 0,
                "results": []
            }
        
        # 실제 사용되는 파라미터만 필터링
        valid_kwargs = {k: v for k, v in kwargs.items() 
                       if v is not None and k in self._data.columns}
        
        if not valid_kwargs:
            return {
                "status": "error", 
                "message": "No valid search parameters",
                "total_count": 0,
                "results": []
            }
        
        # 인덱스 기반 필터링 (복사 없이)
        mask = pd.Series(True, index=self._data.index)
        
        for key, value in valid_kwargs.items():
            if key in self.EXACT_MATCH_FIELDS:
                mask &= (self._data[key] == value)
            else:
                mask &= self._data[key].astype(str).str.contains(
                    str(value), case=False, na=False
                )
        
        result = self._data[mask]
        
        if result.empty:
            return {
                "status": "no_results",
                "message": f"No APIs found with conditions: {valid_kwargs}",
                "total_count": 0,
                "results": []
            }
        
        # 특별 케이스: 단순 개수 조회 (category 또는 subcategory만 있을 때)
        if (len(valid_kwargs) == 1 and 
            ('category' in valid_kwargs or 'subcategory' in valid_kwargs)):
            
            # 간단한 리스트만 반환 (schema 일관성 유지)
            unique_apis = result.drop_duplicates(subset=['api_name'])
            results = []
            for _, api in unique_apis.iterrows():
                results.append({
                    "function_name": api['function_name'],
                    "api_name": api['api_name'],
                    "category": api['category'],
                    "subcategory": api['subcategory']
                })
            
            return {
                "status": "success",
                "message": f"Found {len(result)} APIs ({len(results)} unique)",
                "total_count": len(result),
                "results": results
            }
        
        # 일반 상세 검색 결과
        results = []
        for _, api in result.head(self.MAX_RESULTS).iterrows():
            results.append({
                "function_name": api['function_name'],
                "api_name": api['api_name'],
                "category": api['category'],
                "subcategory": api['subcategory'],
                # 나머지 필드들은 주석처리, 필요 주석해제 후 tool에 인자 추가 필요
                # "description": api['description'],
                # "args": api.get('args', ''),
                # "returns": api.get('returns', ''),
                # "example": api.get('example', ''),
                # "response": api.get('response', ''),
                # "column_mapping": api.get('column_mapping', ''),
                "url_main": api.get('url_main', ''),
                "url_chk": api.get('url_chk', '')
            })
        
        return {
            "status": "success",
            "message": f"Found {len(result)} APIs" + (f" (showing first {self.MAX_RESULTS})" if len(result) > self.MAX_RESULTS else ""),
            "total_count": len(result),
            "results": results
        }
