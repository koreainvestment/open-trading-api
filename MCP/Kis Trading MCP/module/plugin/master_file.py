import logging
import os
import shutil
import requests
from datetime import datetime
from typing import List
from module.plugin.database import Database
from typing import Dict
import pandas as pd

class MasterFileManager:
    """도구별 마스터파일 관리 클래스 (1:N 매핑 지원)"""

    # 툴별 필요한 마스터파일 매핑 (기존 마스터파일들을 툴별로 그룹화)
    TOOL_MASTER_MAPPING = {
        "domestic_stock": [
            "domestic_stock_master",  # 코스닥
            "domestic_stock_kospi_master",  # 코스피
            "domestic_stock_konex_master"  # 코넥스
        ],
        "overseas_stock": [
            "overseas_stock_master",  # 나스닥
            "overseas_stock_nys_master",  # 뉴욕
            "overseas_stock_ams_master",  # 아멕스
            "overseas_stock_shs_master",  # 상해
            "overseas_stock_shi_master",  # 상해지수
            "overseas_stock_szs_master",  # 심천
            "overseas_stock_szi_master",  # 심천지수
            "overseas_stock_tse_master",  # 도쿄
            "overseas_stock_hks_master",  # 홍콩
            "overseas_stock_hnx_master",  # 하노이
            "overseas_stock_hsx_master"  # 호치민
        ],
        "domestic_futureoption": [
            "domestic_future_master",
            "domestic_index_future_master",
            "domestic_cme_future_master",
            "domestic_commodity_future_master",
            "domestic_eurex_option_master"
        ],
        "overseas_futureoption": [
            "overseas_future_master",
            "overseas_index_master"
        ],
        "domestic_bond": [
            "domestic_bond_master"
        ],
        "etfetn": [],  # ETF/ETN 마스터파일 없음
        "elw": [
            "elw_master"
        ],
        "auth": []  # 인증은 마스터파일 불필요
    }

    # 마스터파일별 URL과 처리 함수 매핑 (한국투자증권 기준)
    MASTER_FILE_PROCESS = {
        # 국내주식 마스터파일 (코스닥)
        "domestic_stock_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
            "process": "_MasterFileManager__process_domestic_stock",
            "name_key": "korean_name",
            "code_key": "short_code",
            "ex_value": "kosdaq"
        },

        # 국내주식 마스터파일 (코스피)
        "domestic_stock_kospi_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
            "process": "_MasterFileManager__process_domestic_stock_kospi",
            "name_key": "korean_name",
            "code_key": "short_code",
            "ex_value": "kospi"
        },

        # 국내주식 마스터파일 (코넥스)
        "domestic_stock_konex_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/konex_code.mst.zip",
            "process": "_MasterFileManager__process_domestic_stock_konex",
            "name_key": "stock_name",
            "code_key": "short_code",
            "ex_value": "konex"
        },

        # 해외주식 마스터파일 (나스닥 중심) - 실제 URL 확인됨
        "overseas_stock_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/nasmst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "NAS"
        },
        "overseas_stock_nys_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/nysmst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "NYS"
        },
        "overseas_stock_ams_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/amsmst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "AMS"
        },
        "overseas_stock_shs_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/shsmst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "SHS"
        },
        "overseas_stock_shi_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/shimst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "SHI"
        },
        "overseas_stock_szs_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/szsmst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "SZS"
        },
        "overseas_stock_szi_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/szimst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "SZI"
        },
        "overseas_stock_tse_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/tsemst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "TSE"
        },
        "overseas_stock_hks_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/hksmst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "HKS"
        },
        "overseas_stock_hnx_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/hnxmst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "HNX"
        },
        "overseas_stock_hsx_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/hsxmst.cod.zip",
            "process": "_MasterFileManager__process_overseas_stock",
            "name_key": "korea_name",
            "code_key": "symbol",
            "ex_value": "HSX"
        },

        # 해외지수 마스터파일 (실제 URL 확인됨)
        "overseas_index_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/frgn_code.mst.zip",
            "process": "_MasterFileManager__process_overseas_index",
            "name_key": "korean_name",
            "code_key": "symbol",
            "ex_value": "index"
        },

        # 국내선물 마스터파일 (주식선물옵션)
        "domestic_future_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/fo_stk_code_mts.mst.zip",
            "process": "_MasterFileManager__process_domestic_future",
            "name_key": "korean_name",
            "code_key": "short_code",
            "ex_value": "future"
        },

        # 국내선물 마스터파일 (지수선물옵션)
        "domestic_index_future_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/fo_idx_code_mts.mst.zip",
            "process": "_MasterFileManager__process_domestic_index_future",
            "name_key": "korean_name",
            "code_key": "short_code",
            "ex_value": "index"
        },

        # 국내선물 마스터파일 (CME연계 야간선물)
        "domestic_cme_future_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/fo_cme_code.mst.zip",
            "process": "_MasterFileManager__process_domestic_cme_future",
            "name_key": "korean_name",
            "code_key": "short_code",
            "ex_value": "cme"
        },

        # 국내선물 마스터파일 (상품선물옵션)
        "domestic_commodity_future_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/fo_com_code.mst.zip",
            "process": "_MasterFileManager__process_domestic_commodity_future",
            "name_key": "korean_name",
            "code_key": "short_code",
            "ex_value": "commodity"
        },

        # 국내옵션 마스터파일 (EUREX연계 야간옵션)
        "domestic_eurex_option_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/fo_eurex_code.mst.zip",
            "process": "_MasterFileManager__process_domestic_eurex_option",
            "name_key": "korean_name",
            "code_key": "short_code",
            "ex_value": "eurex"
        },

        # 해외선물 마스터파일 (실제 URL 확인됨)
        "overseas_future_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/ffcode.mst.zip",
            "process": "_MasterFileManager__process_overseas_future",
            "name_key": "korean_name",
            "code_key": "stock_code",
            "ex_value": "future"
        },

        # 국내채권 마스터파일 (실제 URL 확인됨)
        "domestic_bond_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/bond_code.mst.zip",
            "process": "_MasterFileManager__process_domestic_bond",
            "name_key": "bond_name",
            "code_key": "standard_code",
            "ex_value": "bond"
        },

        # ELW 마스터파일 (실제 URL 확인됨)
        "elw_master": {
            "file": "https://new.real.download.dws.co.kr/common/master/elw_code.mst.zip",
            "process": "_MasterFileManager__process_elw",
            "name_key": "korean_name",
            "code_key": "short_code",
            "ex_value": "elw"
        }
    }

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.master_dir = f"./configs/master/{tool_name}"
        self.error_log_path = os.path.join(os.getcwd(), "configs", "master", "error.log")

        # 툴별 필요한 마스터파일 목록 가져오기
        self.required_masters = self.TOOL_MASTER_MAPPING.get(tool_name, [])

        # 마스터 디렉토리 생성
        os.makedirs(self.master_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.error_log_path), exist_ok=True)

        # 데이터베이스 연결 (Singleton 패턴 활용)
        self.db = Database()
        # 필요시에만 초기화 (이미 초기화된 경우 스킵)
        if not self.db.ensure_initialized():
            raise RuntimeError("데이터베이스 초기화에 실패했습니다.")
        self.db_engine = self.db.get_by_name("master")

        # 오류 로그 설정
        self.error_logger = logging.getLogger(f"master_file_error_{self.tool_name}")
        self.error_logger.setLevel(logging.ERROR)  # ERROR 레벨부터 기록

        # 기존 핸들러 제거 (중복 방지)
        for handler in self.error_logger.handlers[:]:
            self.error_logger.removeHandler(handler)

        # 파일 핸들러 추가
        file_handler = logging.FileHandler(self.error_log_path, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)  # ERROR 레벨부터 기록

        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        self.error_logger.addHandler(file_handler)

    def _log(self, level: str, master_file: str, operation: str, message: str):
        """로그 기록 (통합)"""
        log_msg = f"Tool: {self.tool_name}, Master: {master_file}, Operation: {operation}, {level}: {message}"


        if level.lower() == "error":
            self.error_logger.error(log_msg)
        elif level.lower() == "warning":
            self.error_logger.warning(log_msg)
        else:
            self.error_logger.info(log_msg)
    
    @staticmethod
    def get_master_models_for_tool(tool_name: str) -> List:
        """툴별 마스터 모델 목록 반환 (정적 메서드)"""
        from model import ALL_MODELS
        
        # 툴명을 모델 클래스명으로 변환하는 매핑
        tool_to_model_mapping = {
            "domestic_stock": "DomesticStockMaster",
            "overseas_stock": "OverseasStockMaster",
            "domestic_futureoption": "DomesticFutureoptionMaster",
            "overseas_futureoption": "OverseasFutureoptionMaster",
            "domestic_bond": "DomesticBondMaster",
            "etfetn": "EtfetnMaster",
            "elw": "ElwMaster",
            "auth": "AuthMaster"
        }
        
        model_name = tool_to_model_mapping.get(tool_name)
        if not model_name:
            return []
        
        # ALL_MODELS에서 해당하는 모델 클래스 반환
        return [model for model in ALL_MODELS if model.__name__ == model_name]

    # ==============================================
    
    async def ensure_master_file_updated(self, ctx, force_update: bool = False):
        """툴에 필요한 모든 마스터파일 체크 및 업데이트"""
        try:
            # 마스터파일이 필요 없는 툴인 경우 스킵
            if not self.required_masters:
                await ctx.info(f"{self.tool_name} 툴은 마스터파일이 필요하지 않습니다.")
                return

            # 1. 강제 업데이트가 아닌 경우 툴 전체 업데이트 시간 확인
            if not force_update:
                last_update = self.db_engine.get_master_update_time(self.tool_name)
                if last_update and not self.__should_update_from_db(last_update):
                    await ctx.info(f"{self.tool_name} 툴의 마스터파일들이 최신 상태입니다.")
                    return

            # 2. 카테고리 레벨에서 테이블 전체 삭제 (한 번만)
            await self.__clear_category_tables(ctx)

            # 2-1. 해당 폴더의 CSV 파일들 삭제
            await self.__clear_category_csv_files(ctx)

            # 3. 각 마스터파일별로 업데이트 (삭제 없이 추가만)
            total_record_count = 0
            for master_name in self.required_masters:
                record_count = await self.__ensure_single_master_updated(ctx, master_name, force_update)
                total_record_count += record_count

            # 4. 모든 마스터파일 처리 완료 후 툴 전체 업데이트 시간 기록
            if total_record_count > 0:
                self.db_engine.update_master_timestamp(self.tool_name, total_record_count)
                await ctx.info(f"{self.tool_name} 툴의 모든 마스터파일 업데이트 완료 (총 {total_record_count}개 레코드)")

        except Exception as e:
            # 오류 로그 기록
            self._log("error", "all_masters", "check_update", str(e))
            await ctx.error(f"마스터파일 체크 실패: {str(e)}")
            raise

    def is_master_file_available(self) -> bool:
        """마스터파일들이 사용 가능한지 확인"""
        try:
            # 마스터파일이 필요 없는 툴인 경우 True 반환
            if not self.required_masters:
                return True
            
            # 툴별 모델에서 데이터가 있는지 확인 (여러 마스터파일이 하나의 모델로 통합됨)
            master_models = self.get_master_models_for_tool(self.tool_name)
            
            for model_class in master_models:
                # 데이터베이스에서 레코드 수 확인
                record_count = self.db_engine.count(model_class)
                if record_count == 0:
                    return False
                    
            return True
            
        except Exception as e:
            self._log("error", "all_masters", "check_availability", str(e))
            return False

    # def get_master_file_paths(self, master_name: str) -> str:
    #     """마스터파일 경로 반환"""
    #     return os.path.join(self.master_dir, f"{master_name}.tmp")

    async def __ensure_single_master_updated(self, ctx, master_name: str, force_update: bool = False) -> int:
        """단일 마스터파일 체크 및 업데이트"""
        # 마스터파일 다운로드 및 DB 저장
        await ctx.info(f"{master_name} 마스터파일 업데이트 중...")

        try:
            # 1. URL 확인
            master_config = self.MASTER_FILE_PROCESS.get(master_name)
            if not master_config:
                raise Exception(f"{master_name}에 대한 마스터파일 설정이 없습니다.")
            
            master_url = master_config["file"]

            # 2. 임시 파일로 다운로드
            temp_file = os.path.join(self.master_dir, f"{master_name}.tmp")
            await ctx.info(f"마스터파일 다운로드 중: {master_name}")

            success = await self.__download_file(master_url, temp_file)
            if not success:
                raise Exception(f"{master_name} 마스터파일 다운로드 실패")

            # 3. 파일 가공 (마스터파일별 특화 로직) - DataFrame 반환
            import pandas as pd

            # MASTER_FILE_PROCESS에서 처리 함수명 가져오기
            process_func_name = master_config.get("process")
            if process_func_name:
                try:
                    # 처리 함수 가져오기
                    process_func = getattr(self, process_func_name)
                    # 가공 함수에서 DataFrame 반환받기
                    df = await process_func(temp_file, ctx)
                except Exception as e:
                    # 오류 로그 기록
                    self._log("error", master_name, "process", str(e))
                    await ctx.error(f"마스터파일 가공 실패: {master_name}, 오류: {str(e)}")
                    # 빈 DataFrame 반환
                    df = pd.DataFrame()
            else:
                # 기본 처리 - 빈 DataFrame 반환
                await ctx.warning(f"지원하지 않는 마스터파일: {master_name}")
                df = pd.DataFrame()

            # 4. CSV 파일 저장
            await ctx.info(f"CSV 파일 저장 중: {master_name} ({len(df)}개 레코드)")
            csv_saved = await self.__save_csv_file(df, master_name, ctx)

            # 5. 모델에 저장
            await ctx.info(f"모델에 저장 중: {master_name} ({len(df)}개 레코드)")

            # 5-1. 모델용 데이터 변환
            model_data = self.__convert_to_model_data(df, master_name)

            # 5-2. 모델에 저장
            try:
                model_class = self.__get_model_class(master_name)
                if not model_class:
                    raise Exception(f"{master_name}에 대한 모델 클래스를 찾을 수 없습니다.")
                
                # bulk_replace_master_data 사용 (카테고리 레벨에서 이미 삭제되었으므로 INSERT만)
                record_count = self.db_engine.bulk_replace_master_data(
                    model_class=model_class,
                    data_list=model_data,
                    master_name=master_name
                )
            except Exception as e:
                # 에러 로깅 시스템에 기록
                self._log("error", master_name, "bulk_replace_master_data", str(e))
                raise

            await ctx.info(f"데이터베이스 저장 완료: {master_name} ({record_count}개 레코드)")

            # 6. 임시 파일 정리 (보존)
            # if os.path.exists(temp_file):
            #     os.remove(temp_file)

            await ctx.info(f"{master_name} 마스터파일 업데이트 완료")
            return record_count

        except Exception as e:
            # 오류 로그 기록
            self._log("error", master_name, "download_and_save", str(e))
            # 임시 파일 정리 (보존)
            # temp_file = os.path.join(self.master_dir, f"{master_name}.tmp")
            # if os.path.exists(temp_file):
            #     os.remove(temp_file)
            raise

    def __should_update_from_db(self, last_update: datetime) -> bool:
        """DB 기반 업데이트 필요 여부 확인"""
        try:
            return last_update.date() < datetime.now().date()
        except (ValueError, AttributeError):
            return True  # 날짜 파싱 실패 시 업데이트

    async def __clear_category_tables(self, ctx):
        """카테고리 레벨에서 해당 툴의 모든 테이블 데이터 삭제"""
        try:
            # 툴별 모델 클래스들 가져오기
            master_models = self.get_master_models_for_tool(self.tool_name)
            
            if not master_models:
                await ctx.info(f"{self.tool_name} 툴에 해당하는 모델이 없습니다.")
                return
            
            # 각 모델의 테이블 데이터 삭제
            for model_class in master_models:
                try:
                    # 기존 데이터 개수 확인
                    before_count = self.db_engine.count(model_class)
                    
                    # 테이블 전체 삭제
                    session = self.db_engine.get_session()
                    try:
                        deleted_count = session.query(model_class).delete()
                        session.commit()
                        await ctx.info(f"{model_class.__name__} 테이블 데이터 삭제 완료: {deleted_count}개 레코드")
                    finally:
                        session.close()
                        
                except Exception as e:
                    self._log("error", model_class.__name__, "clear_table", str(e))
                    await ctx.error(f"{model_class.__name__} 테이블 삭제 실패: {str(e)}")
                    raise
                    
        except Exception as e:
            self._log("error", "all_models", "clear_category_tables", str(e))
            await ctx.error(f"카테고리 테이블 삭제 실패: {str(e)}")
            raise

    async def __clear_category_csv_files(self, ctx):
        """카테고리 레벨에서 해당 툴의 모든 CSV 파일 및 임시 파일 삭제"""
        try:
            import glob
            
            # 해당 툴의 마스터 디렉토리 경로
            master_dir = self.master_dir
            
            if not os.path.exists(master_dir):
                await ctx.info(f"마스터 디렉토리가 존재하지 않습니다: {master_dir}")
                return
            
            # CSV 파일 패턴으로 검색
            csv_pattern = os.path.join(master_dir, "*.csv")
            csv_files = glob.glob(csv_pattern)
            
            # 임시 파일 패턴으로 검색 (.tmp, .tmp.zip 등)
            tmp_patterns = [
                os.path.join(master_dir, "*.tmp"),
                os.path.join(master_dir, "*.tmp.*"),
                os.path.join(master_dir, "*_part*.tmp"),
                os.path.join(master_dir, "*_part*.tmp.*")
            ]
            
            tmp_files = []
            for pattern in tmp_patterns:
                tmp_files.extend(glob.glob(pattern))
            
            all_files = csv_files + tmp_files
            
            if not all_files:
                await ctx.info(f"삭제할 파일이 없습니다: {master_dir}")
                return
            
            # 파일들 삭제
            deleted_count = 0
            for file_path in all_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    file_type = "CSV" if file_path.endswith('.csv') else "TMP"
                    await ctx.info(f"{file_type} 파일 삭제: {os.path.basename(file_path)}")
                except Exception as e:
                    self._log("error", os.path.basename(file_path), "delete_file", str(e))
                    await ctx.warning(f"파일 삭제 실패: {os.path.basename(file_path)} - {str(e)}")
            
            await ctx.info(f"파일 삭제 완료: {deleted_count}개 파일 (CSV + TMP)")
                    
        except Exception as e:
            self._log("error", "all_files", "clear_category_csv_files", str(e))
            await ctx.error(f"카테고리 파일 삭제 실패: {str(e)}")
            raise

    def __get_model_class(self, master_name: str):
        """마스터파일명에 해당하는 모델 클래스 반환 - TOOL_MASTER_MAPPING 활용"""
        # TOOL_MASTER_MAPPING을 역방향으로 검색하여 마스터파일이 속한 툴 찾기
        for tool_name, master_files in self.TOOL_MASTER_MAPPING.items():
            if master_name in master_files:
                # 해당 툴의 모델 클래스들 가져오기
                master_models = self.get_master_models_for_tool(tool_name)
                if master_models:
                    # 첫 번째 모델 클래스 반환 (각 툴당 하나의 모델만 있음)
                    return master_models[0]
        
        # 마스터파일이 TOOL_MASTER_MAPPING에 없는 경우 None 반환
        return None

    async def __download_file(self, url: str, file_path: str) -> bool:
        """파일 다운로드 (ZIP 파일 지원)"""
        try:
            import zipfile
            import ssl

            # SSL 컨텍스트 설정 (한국투자증권 서버용)
            ssl._create_default_https_context = ssl._create_unverified_context

            response = requests.get(url, timeout=60)  # 대용량 파일을 위해 타임아웃 증가
            response.raise_for_status()

            # ZIP 파일인지 확인
            if url.endswith('.zip'):
                # ZIP 파일로 저장
                zip_file_path = file_path + '.zip'
                with open(zip_file_path, 'wb') as f:
                    f.write(response.content)

                # ZIP 파일 압축 해제
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(file_path))

                # 압축 해제된 파일명 찾기
                extracted_files = zip_ref.namelist()
                if extracted_files:
                    # .mst 파일 찾기
                    mst_file = next((f for f in extracted_files if f.endswith('.mst')), extracted_files[0])
                    extracted_path = os.path.join(os.path.dirname(file_path), mst_file)

                    # 원본 파일명으로 이동
                    if extracted_path != file_path:
                        shutil.move(extracted_path, file_path)

                # ZIP 파일 삭제
                os.remove(zip_file_path)
            else:
                # 일반 파일로 저장
                with open(file_path, 'wb') as f:
                    f.write(response.content)

            return True
        except Exception as e:
            # 오류 로그 기록
            master_file = os.path.basename(file_path)
            self._log("error", master_file, "download", str(e))
            return False

    def __get_master_update_status(self, master_name: str = None):
        """마스터파일 업데이트 상태 조회"""
        if master_name:
            last_update = self.db_engine.get_master_update_time(master_name)
            model_class = self.__get_model_class(master_name)
            record_count = 0
            if model_class:
                record_count = self.db_engine.count(model_class)

            return {
                "master_name": master_name,
                "last_updated": last_update,
                "record_count": record_count,
                "needs_update": self.__should_update_from_db(last_update) if last_update else True
            }

        # 툴 전체 상태 조회
        last_update = self.db_engine.get_master_update_time(self.tool_name)
        total_record_count = 0
        
        # 툴의 모든 마스터 모델에서 레코드 수 합계
        master_models = self.get_master_models_for_tool(self.tool_name)
        for model_class in master_models:
            total_record_count += self.db_engine.count(model_class)

        return {
            "tool_name": self.tool_name,
            "last_updated": last_update,
            "total_record_count": total_record_count,
            "needs_update": self.__should_update_from_db(last_update) if last_update else True,
            "master_files": self.required_masters
        }

    # ========== 공통 유틸리티 메서드들 ==========
    
    async def _read_file_with_encoding(self, file_path: str, ctx) -> str:
        """여러 인코딩을 시도하여 파일 읽기"""
        encodings = ['cp949', 'euc-kr', 'utf-8', 'utf-8-sig', 'iso-8859-1', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, mode="r", encoding=encoding) as f:
                    content = f.read()
                await ctx.info(f"파일을 {encoding} 인코딩으로 성공적으로 읽었습니다.")
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                await ctx.warning(f"{encoding} 인코딩 시도 중 오류: {str(e)}")
                continue
        
        raise Exception("모든 인코딩 시도 실패")
    
    def _create_dataframe(self, data, columns):
        """DataFrame 생성 및 공통 처리"""
        import pandas as pd
        
        df = pd.DataFrame(data, columns=columns)
        df = df.astype(str)
        df = df.replace(['nan', 'NaN', 'None', 'null'], '')
        return df
    
    def _read_csv_with_encoding(self, file_path: str, **kwargs):
        """여러 인코딩을 시도하여 CSV 파일 읽기"""
        import pandas as pd
        
        encodings = ['cp949', 'euc-kr', 'utf-8', 'utf-8-sig', 'iso-8859-1', 'latin1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, **kwargs)
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
        
        raise Exception("모든 인코딩 시도 실패")
    
    def _read_fwf_with_encoding(self, file_path: str, **kwargs):
        """여러 인코딩을 시도하여 고정폭 파일 읽기"""
        import pandas as pd
        
        encodings = ['cp949', 'euc-kr', 'utf-8', 'utf-8-sig', 'iso-8859-1', 'latin1']
        
        for encoding in encodings:
            try:
                df = pd.read_fwf(file_path, encoding=encoding, **kwargs)
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
        
        raise Exception("모든 인코딩 시도 실패")

    def __convert_to_model_data(self, df, master_name: str) -> List[Dict]:
        """DataFrame을 모델용 데이터로 변환 - MASTER_FILE_PROCESS의 name_key, code_key, ex_value 사용"""
        try:
            model_data = []
            
            # MASTER_FILE_PROCESS에서 name_key, code_key, ex_value 가져오기
            master_config = self.MASTER_FILE_PROCESS.get(master_name, {})
            name_key = master_config.get("name_key", "name")
            code_key = master_config.get("code_key", "code")
            ex_value = master_config.get("ex_value", "")
            
            for _, row in df.iterrows():
                # 지정된 키로 종목명과 종목코드 추출
                name = None
                code = None
                
                # 종목명 추출 (띄어쓰기 제거)
                if name_key in row and pd.notna(row[name_key]) and str(row[name_key]).strip():
                    name_str = str(row[name_key]).strip()
                    if name_str not in ['nan', 'NaN', 'None', 'null', '']:
                        name = name_str.replace(" ", "")
                
                # 종목코드 추출
                if code_key in row and pd.notna(row[code_key]) and str(row[code_key]).strip():
                    code_str = str(row[code_key]).strip()
                    if code_str not in ['nan', 'NaN', 'None', 'null', '']:
                        code = code_str
                
                # 유효한 데이터만 추가
                if name and code:
                    model_data.append({
                        'name': name,
                        'code': code,
                        'ex': ex_value
                    })
            
            return model_data
            
        except Exception as e:
            self._log("error", master_name, "convert_to_model_data", str(e))
            return []

    async def __save_csv_file(self, df, master_name: str, ctx) -> bool:
        """DataFrame을 CSV 파일로 저장"""
        try:
            if df.empty:
                await ctx.warning(f"빈 DataFrame으로 CSV 파일을 생성하지 않습니다: {master_name}")
                return False
            
            # CSV 저장 전 추가 nan 처리
            df_clean = df.copy()
            df_clean = df_clean.replace(['nan', 'NaN', 'None', 'null'], '')
            
            # CSV 파일 경로 설정
            csv_file_path = os.path.join(self.master_dir, f"{master_name}.csv")
            
            # CSV 파일 저장 (UTF-8 BOM 인코딩으로 한글 지원)
            df_clean.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
            
            await ctx.info(f"CSV 파일 저장 완료: {csv_file_path} ({len(df_clean)}개 레코드)")
            return True
            
        except Exception as e:
            self._log("error", master_name, "save_csv", str(e))
            await ctx.error(f"CSV 파일 저장 실패: {master_name}, 오류: {str(e)}")
            return False
    


    # ========== 마스터파일별 특화 가공 메서드들 ==========

    async def __process_domestic_stock(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내주식 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내주식 마스터파일 가공 중...")

        try:
            import pandas as pd
            import os

            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)

            # 원본 코드와 정확히 동일한 파싱
            tmp_fil1 = raw_file.replace('.tmp', '_part1.tmp')
            tmp_fil2 = raw_file.replace('.tmp', '_part2.tmp')
            wf1 = open(tmp_fil1, mode="w")
            wf2 = open(tmp_fil2, mode="w")

            # 파일 내용을 라인별로 처리
            for row in file_content.splitlines():
                rf1 = row[0:len(row) - 222]
                rf1_1 = rf1[0:9].rstrip()
                rf1_2 = rf1[9:21].rstrip()
                rf1_3 = rf1[21:].strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
                rf2 = row[-222:]
                wf2.write(rf2)

            wf1.close()
            wf2.close()

            part1_columns = ['short_code', 'standard_code', 'korean_name']
            df1 = self._read_csv_with_encoding(tmp_fil1, header=None, names=part1_columns, dtype=str)

            field_specs = [2, 1,
                           4, 4, 4, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 9,
                           5, 5, 1, 1, 1,
                           2, 1, 1, 1, 2,
                           2, 2, 3, 1, 3,
                           12, 12, 8, 15, 21,
                           2, 7, 1, 1, 1,
                           1, 9, 9, 9, 5,
                           9, 8, 9, 3, 1,
                           1, 1
                           ]

            part2_columns = ['security_group_code', 'market_cap_scale_code',
                             'industry_large_code', 'industry_medium_code', 'industry_small_code', 'venture_company_yn',
                             'low_liquidity_yn', 'krx_stock_yn', 'etp_product_code', 'krx100_stock_yn',
                             'krx_auto_yn', 'krx_semiconductor_yn', 'krx_bio_yn', 'krx_bank_yn', 'spac_yn',
                             'krx_energy_chemical_yn', 'krx_steel_yn', 'short_term_overheat_code', 'krx_media_telecom_yn',
                             'krx_construction_yn', 'kosdaq_investment_caution_yn', 'krx_security_division', 'krx_ship_division',
                             'krx_sector_insurance_yn', 'krx_sector_transport_yn', 'kosdaq150_index_yn', 'stock_base_price',
                             'regular_market_unit', 'after_hours_market_unit', 'trading_halt_yn', 'liquidation_yn',
                             'management_stock_yn', 'market_warning_code', 'market_warning_risk_yn', 'dishonest_disclosure_yn',
                             'bypass_listing_yn', 'lock_division_code', 'par_value_change_code', 'capital_increase_code', 'margin_rate',
                             'credit_order_yn', 'credit_period', 'prev_day_volume', 'stock_par_value', 'stock_listing_date', 'listed_shares_thousand',
                             'capital', 'settlement_month', 'public_offering_price', 'preferred_stock_code', 'short_sale_overheat_yn', 'unusual_rise_yn',
                             'krx300_stock_yn', 'sales', 'operating_profit', 'ordinary_profit', 'net_income', 'roe',
                             'base_year_month', 'prev_day_market_cap_billion', 'group_company_code', 'company_credit_limit_exceed_yn', 'collateral_loan_yn', 'securities_lending_yn'
                             ]

            df2 = self._read_fwf_with_encoding(tmp_fil2, widths=field_specs, names=part2_columns)

            df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)
            
            # 공통 DataFrame 처리
            df = df.astype(str)
            df = df.replace(['nan', 'NaN', 'None', 'null'], '')

            # clean temporary file and dataframe
            del (df1)
            del (df2)
            os.remove(tmp_fil1)
            os.remove(tmp_fil2)

            await ctx.info(f"국내주식 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_stock_master", "process", str(e))
            await ctx.error(f"국내주식 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_domestic_stock_kospi(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내주식 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내주식 마스터파일 가공 중...")

        try:
            import pandas as pd
            import os

            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)

            # 원본 코드와 정확히 동일한 파싱
            tmp_fil1 = raw_file.replace('.tmp', '_part1.tmp')
            tmp_fil2 = raw_file.replace('.tmp', '_part2.tmp')
            wf1 = open(tmp_fil1, mode="w")
            wf2 = open(tmp_fil2, mode="w")

            # 파일 내용을 라인별로 처리
            for row in file_content.splitlines():
                rf1 = row[0:len(row) - 228]
                rf1_1 = rf1[0:9].rstrip()
                rf1_2 = rf1[9:21].rstrip()
                rf1_3 = rf1[21:].strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
                rf2 = row[-228:]
                wf2.write(rf2)

            wf1.close()
            wf2.close()

            part1_columns = ['short_code', 'standard_code', 'korean_name']
            df1 = self._read_csv_with_encoding(tmp_fil1, header=None, names=part1_columns, dtype=str)

            field_specs = [2, 1, 4, 4, 4,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 1, 1, 1, 1,
                           1, 9, 5, 5, 1,
                           1, 1, 2, 1, 1,
                           1, 2, 2, 2, 3,
                           1, 3, 12, 12, 8,
                           15, 21, 2, 7, 1,
                           1, 1, 1, 1, 9,
                           9, 9, 5, 9, 8,
                           9, 3, 1, 1, 1
                           ]

            part2_columns = ['group_code', 'market_cap_scale', 'industry_large', 'industry_medium', 'industry_small',
                             'manufacturing', 'low_liquidity', 'governance_index_stock', 'kospi200_sector_industry', 'kospi100',
                             'kospi50', 'krx', 'etp', 'elw_issuance', 'krx100',
                             'krx_auto', 'krx_semiconductor', 'krx_bio', 'krx_bank', 'spac',
                             'krx_energy_chemical', 'krx_steel', 'short_term_overheat', 'krx_media_telecom', 'krx_construction',
                             'non1', 'krx_security', 'krx_ship', 'krx_sector_insurance', 'krx_sector_transport',
                             'sri', 'base_price', 'trading_unit', 'after_hours_unit', 'trading_halt',
                             'liquidation', 'management_stock', 'market_warning', 'warning_forecast', 'dishonest_disclosure',
                             'bypass_listing', 'lock_division', 'par_value_change', 'capital_increase', 'margin_rate',
                             'credit_available', 'credit_period', 'prev_day_volume', 'par_value', 'listing_date',
                             'listed_shares', 'capital', 'settlement_month', 'public_offering_price', 'preferred_stock',
                             'short_sale_overheat', 'unusual_rise', 'krx300', 'kospi', 'sales',
                             'operating_profit', 'ordinary_profit', 'net_income', 'roe', 'base_year_month',
                             'market_cap', 'group_company_code', 'company_credit_limit_exceed', 'collateral_loan_available', 'securities_lending_available'
                             ]

            df2 = self._read_fwf_with_encoding(tmp_fil2, widths=field_specs, names=part2_columns)

            df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)
            
            # 공통 DataFrame 처리
            df = df.astype(str)
            df = df.replace(['nan', 'NaN', 'None', 'null'], '')

            # clean temporary file and dataframe
            del (df1)
            del (df2)
            os.remove(tmp_fil1)
            os.remove(tmp_fil2)

            await ctx.info(f"국내주식 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_stock_kospi_master", "process", str(e))
            await ctx.error(f"국내주식 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_domestic_stock_konex(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내주식 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내주식 마스터파일 가공 중...")

        try:
            import pandas as pd

            # 원본 코드와 정확히 동일한 파싱
            await ctx.info("복잡한 고정폭 텍스트 파일 파싱 중...")
            
            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)
            lines = file_content.splitlines()

            data = []
            for row in lines:
                row = row.strip()
                mksc_shrn_iscd = row[0:9].strip()
                stnd_iscd = row[9:21].strip()
                scrt_grp_cls_code = row[-184:-182].strip()
                stck_sdpr = row[-182:-173].strip()
                frml_mrkt_deal_qty_unit = row[-173:-168].strip()
                ovtm_mrkt_deal_qty_unit = row[-168:-163].strip()
                trht_yn = row[-163:-162].strip()
                sltr_yn = row[-162:-161].strip()
                mang_issu_yn = row[-161:-160].strip()
                mrkt_alrm_cls_code = row[-160:-158].strip()
                mrkt_alrm_risk_adnt_yn = row[-158:-157].strip()
                insn_pbnt_yn = row[-157:-156].strip()
                byps_lstn_yn = row[-156:-155].strip()
                flng_cls_code = row[-155:-153].strip()
                fcam_mod_cls_code = row[-153:-151].strip()
                icic_cls_code = row[-151:-149].strip()
                marg_rate = row[-149:-146].strip()
                crdt_able = row[-146:-145].strip()
                crdt_days = row[-145:-142].strip()
                prdy_vol = row[-142:-130].strip()
                stck_fcam = row[-130:-118].strip()
                stck_lstn_date = row[-118:-110].strip()
                lstn_stcn = row[-110:-95].strip()
                cpfn = row[-95:-74].strip()
                stac_month = row[-74:-72].strip()
                po_prc = row[-72:-65].strip()
                prst_cls_code = row[-65:-64].strip()
                ssts_hot_yn = row[-64:-63].strip()
                stange_runup_yn = row[-63:-62].strip()
                krx300_issu_yn = row[-62:-61].strip()
                sale_account = row[-61:-52].strip()
                bsop_prfi = row[-52:-43].strip()
                op_prfi = row[-43:-34].strip()
                thtr_ntin = row[-34:-29].strip()
                roe = row[-29:-20].strip()
                base_date = row[-20:-12].strip()
                prdy_avls_scal = row[-12:-3].strip()
                co_crdt_limt_over_yn = row[-3:-2].strip()
                secu_lend_able_yn = row[-2:-1].strip()
                stln_able_yn = row[-1:].strip()
                hts_kor_isnm = row[21:-184].strip()

                data.append([mksc_shrn_iscd, stnd_iscd, hts_kor_isnm, scrt_grp_cls_code,
                             stck_sdpr, frml_mrkt_deal_qty_unit, ovtm_mrkt_deal_qty_unit,
                             trht_yn, sltr_yn, mang_issu_yn, mrkt_alrm_cls_code,
                             mrkt_alrm_risk_adnt_yn, insn_pbnt_yn, byps_lstn_yn,
                             flng_cls_code, fcam_mod_cls_code, icic_cls_code, marg_rate,
                             crdt_able, crdt_days, prdy_vol, stck_fcam, stck_lstn_date,
                             lstn_stcn, cpfn, stac_month, po_prc, prst_cls_code, ssts_hot_yn,
                             stange_runup_yn, krx300_issu_yn, sale_account, bsop_prfi,
                             op_prfi, thtr_ntin, roe, base_date, prdy_avls_scal,
                             co_crdt_limt_over_yn, secu_lend_able_yn, stln_able_yn])

            columns = ['short_code', 'standard_code', 'stock_name', 'security_group_code', 'stock_base_price',
                       'regular_market_unit', 'after_hours_market_unit', 'trading_halt_yn',
                       'liquidation_yn', 'management_stock_yn', 'market_warning_code', 'market_warning_risk_yn',
                       'dishonest_disclosure_yn', 'bypass_listing_yn', 'lock_division_code', 'par_value_change_code',
                       'capital_increase_code', 'margin_rate', 'credit_order_yn', 'credit_period', 'prev_day_volume',
                       'stock_par_value', 'stock_listing_date', 'listed_shares_thousand', 'capital', 'settlement_month', 'public_offering_price',
                       'preferred_stock_code', 'short_sale_overheat_yn', 'unusual_rise_yn', 'krx300_stock_yn',
                       'sales', 'operating_profit', 'ordinary_profit', 'net_income', 'roe', 'base_year_month', 'prev_day_market_cap_billion',
                       'company_credit_limit_exceed_yn', 'collateral_loan_yn', 'securities_lending_yn']
            
            # 공통 DataFrame 처리
            df = self._create_dataframe(data, columns)

            await ctx.info(f"국내주식 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_stock_konex_master", "process", str(e))
            await ctx.error(f"국내주식 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_overseas_stock(self, raw_file: str, ctx) -> pd.DataFrame:
        """해외주식 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("해외주식 마스터파일 가공 중...")

        try:
            import pandas as pd

            # 원본 코드와 정확히 동일한 파싱
            columns = ['national_code', 'exchange_id', 'exchange_code', 'exchange_name', 'symbol', 'realtime_symbol',
                       'korea_name', 'english_name', 'security_type', 'currency',
                       'float_position', 'data_type', 'base_price', 'bid_order_size', 'ask_order_size',
                       'market_start_time', 'market_end_time', 'dr_yn', 'dr_country_code', 'industry_classification_code',
                       'index_constituent_yn', 'tick_size_type',
                       'classification_code',
                       'tick_size_type_detail']

            # 파일 읽기 (공통 로직)
            df = self._read_csv_with_encoding(raw_file, sep='\t', dtype=str)
            df.columns = columns
            
            # 공통 DataFrame 처리
            df = df.astype(str)
            df = df.replace(['nan', 'NaN', 'None', 'null'], '')

            await ctx.info(f"해외주식 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "overseas_stock_master", "process", str(e))
            await ctx.error(f"해외주식 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_overseas_index(self, raw_file: str, ctx) -> pd.DataFrame:
        """해외지수 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("해외지수 마스터파일 가공 중...")

        try:
            import pandas as pd
            import os

            # 원본 코드와 정확히 동일한 파싱
            tmp_fil1 = raw_file.replace('.tmp', '_part1.tmp')
            tmp_fil2 = raw_file.replace('.tmp', '_part2.tmp')
            wf1 = open(tmp_fil1, mode="w")
            wf2 = open(tmp_fil2, mode="w")

            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)
            
            # 파일 내용을 라인별로 처리
            for row in file_content.splitlines():
                if row[0:1] == 'X':
                    rf1 = row[0:len(row) - 14]
                    rf_1 = rf1[0:1]
                    rf1_2 = rf1[1:11]
                    rf1_3 = rf1[11:40].replace(",", "")
                    rf1_4 = rf1[40:80].replace(",", "").strip()
                    wf1.write(rf_1 + ',' + rf1_2 + ',' + rf1_3 + ',' + rf1_4 + '\n')
                    rf2 = row[-15:]
                    wf2.write(rf2 + '\n')
                    continue
                rf1 = row[0:len(row) - 14]
                rf1_1 = rf1[0:1]
                rf1_2 = rf1[1:11]
                rf1_3 = rf1[11:50].replace(",", "")
                rf1_4 = row[50:75].replace(",", "").strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + ',' + rf1_4 + '\n')
                rf2 = row[-15:]
                wf2.write(rf2 + '\n')

            wf1.close()
            wf2.close()

            part1_columns = ['division_code', 'symbol', 'english_name', 'korean_name']
            df1 = self._read_csv_with_encoding(tmp_fil1, header=None, names=part1_columns, dtype=str)

            field_specs = [4, 1, 1, 1, 4, 3]
            part2_columns = ['industry_code', 'dow30_inclusion_yn', 'nasdaq100_inclusion_yn', 'sp500_inclusion_yn', 'exchange_code', 'country_division_code']
            df2 = self._read_fwf_with_encoding(tmp_fil2, widths=field_specs, names=part2_columns)
            df2['industry_code'] = df2['industry_code'].str.replace(pat=r'[^A-Z]', repl=r'', regex=True)
            df2['dow30_inclusion_yn'] = df2['dow30_inclusion_yn'].str.replace(pat=r'[^0-1]+', repl=r'', regex=True)
            df2['nasdaq100_inclusion_yn'] = df2['nasdaq100_inclusion_yn'].str.replace(pat=r'[^0-1]+', repl=r'', regex=True)
            df2['sp500_inclusion_yn'] = df2['sp500_inclusion_yn'].str.replace(pat=r'[^0-1]+', repl=r'', regex=True)

            DF = pd.concat([df1, df2], axis=1)
            
            # 공통 DataFrame 처리
            DF = DF.astype(str)
            DF = DF.replace(['nan', 'NaN', 'None', 'null'], '')

            # 임시 파일들 정리
            os.remove(tmp_fil1)
            os.remove(tmp_fil2)

            # DataFrame 직접 반환 (CSV 저장 제거됨)

            await ctx.info(f"해외지수 마스터파일 가공 완료: {len(DF)}개 종목")
            return DF

        except Exception as e:
            self._log("error", "overseas_index_master", "process", str(e))
            await ctx.error(f"해외지수 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_domestic_future(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내선물 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내선물 마스터파일 가공 중...")

        try:
            import pandas as pd

            # 원본 코드와 정확히 동일한 파싱
            columns = ['product_type', 'short_code', 'standard_code', 'korean_name', 'atm_division',
                       'strike_price', 'maturity_division_code', 'underlying_short_code', 'underlying_name']
            
            # 파일 읽기 (공통 로직)
            df = self._read_csv_with_encoding(raw_file, sep='|', header=None, dtype=str)
            df.columns = columns
            
            # 공통 DataFrame 처리
            df = df.astype(str)
            df = df.replace(['nan', 'NaN', 'None', 'null'], '')

            # DataFrame 직접 반환 (CSV 저장 제거됨)

            await ctx.info(f"국내선물 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_future_master", "process", str(e))
            await ctx.error(f"국내선물 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_domestic_index_future(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내지수선물 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내지수선물 마스터파일 가공 중...")

        try:
            import pandas as pd

            # 원본 코드와 정확히 동일한 파싱
            columns = ['product_type', 'short_code', 'standard_code', 'korean_name', 'atm_division',
                       'strike_price', 'maturity_division_code', 'underlying_short_code', 'underlying_name']
            
            # 파일 읽기 (공통 로직)
            df = self._read_csv_with_encoding(raw_file, sep='|', header=None, dtype=str)
            df.columns = columns
            
            # 공통 DataFrame 처리
            df = df.astype(str)
            df = df.replace(['nan', 'NaN', 'None', 'null'], '')

            # DataFrame 직접 반환 (CSV 저장 제거됨)

            await ctx.info(f"국내지수선물 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_index_future_master", "process", str(e))
            await ctx.error(f"국내지수선물 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_domestic_cme_future(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내CME연계 야간선물 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내CME연계 야간선물 마스터파일 가공 중...")

        try:
            import pandas as pd

            # 원본 코드와 정확히 동일한 파싱
            columns = ['product_type', 'short_code', 'standard_code', 'korean_name', 'strike_price', 'underlying_short_code', 'underlying_name']
            df = pd.DataFrame(columns=columns)
            ridx = 1

            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)
            
            # 파일 내용을 라인별로 처리
            for row in file_content.splitlines():
                a = row[0:1]
                b = row[1:10].strip()
                c = row[10:22].strip()
                d = row[22:63].strip()
                e = row[63:72].strip()
                f = row[72:81].strip()
                g = row[81:].strip()
                df.loc[ridx] = [a, b, c, d, e, f, g]
                ridx += 1

            # DataFrame 직접 반환 (CSV 저장 제거됨)

            await ctx.info(f"국내CME연계 야간선물 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_cme_future_master", "process", str(e))
            await ctx.error(f"국내CME연계 야간선물 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_domestic_commodity_future(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내상품선물 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내상품선물 마스터파일 가공 중...")

        try:
            import pandas as pd
            import os

            # 원본 코드와 정확히 동일한 파싱
            # df1 : '상품구분','상품종류','단축코드','표준코드','한글종목명'
            tmp_fil1 = raw_file.replace('.tmp', '_part1.tmp')
            tmp_fil2 = raw_file.replace('.tmp', '_part2.tmp')
            wf1 = open(tmp_fil1, mode="w")
            wf2 = open(tmp_fil2, mode="w")

            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)
            
            # 파일 내용을 라인별로 처리
            for row in file_content.splitlines():
                rf1 = row[0:55]
                rf1_1 = rf1[0:1]
                rf1_2 = rf1[1:2]
                rf1_3 = rf1[2:11].strip()
                rf1_4 = rf1[11:23].strip()
                rf1_5 = rf1[23:55].strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + ',' + rf1_4 + ',' + rf1_5 + '\n')
                rf2 = row[55:].lstrip()
                wf2.write(rf2)

            wf1.close()
            wf2.close()

            part1_columns = ['product_division', 'product_type', 'short_code', 'standard_code', 'korean_name']
            df1 = self._read_csv_with_encoding(tmp_fil1, header=None, names=part1_columns)

            # df2 : '월물구분코드','기초자산 단축코드','기초자산 명'
            tmp_fil3 = raw_file.replace('.tmp', '_part3.tmp')
            wf3 = open(tmp_fil3, mode="w")

            # tmp_fil2 읽기 (공통 함수 사용)
            tmp_fil2_content = await self._read_file_with_encoding(tmp_fil2, ctx)
            for row in tmp_fil2_content.splitlines():
                rf2 = row[:]
                rf2_1 = rf2[8:9]
                rf2_2 = rf2[9:12]
                rf2_3 = rf2[12:].strip()
                wf3.write(rf2_1 + ',' + rf2_2 + ',' + rf2_3 + '\n')

            wf3.close()

            part2_columns = ['maturity_division_code', 'underlying_short_code', 'underlying_name']
            df2 = self._read_csv_with_encoding(tmp_fil3, header=None, names=part2_columns)

            # DF : df1 + df2
            df = pd.concat([df1, df2], axis=1)

            # 임시 파일들 정리
            for tmp_file in [tmp_fil1, tmp_fil2, tmp_fil3]:
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)

            # DataFrame 직접 반환 (CSV 저장 제거됨)

            await ctx.info(f"국내상품선물 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_commodity_future_master", "process", str(e))
            await ctx.error(f"국내상품선물 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_domestic_eurex_option(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내EUREX연계 야간옵션 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내EUREX연계 야간옵션 마스터파일 가공 중...")

        try:
            import pandas as pd
            import os

            # 파일이 존재하지 않는 경우 빈 DataFrame 반환
            if not os.path.exists(raw_file):
                await ctx.warning(f"파일이 존재하지 않습니다: {raw_file}")
                return pd.DataFrame()

            # 원본 코드와 정확히 동일한 파싱
            # df1 : '상품종류','단축코드','표준코드','한글종목명'
            tmp_fil1 = raw_file.replace('.tmp', '_part1.tmp')
            tmp_fil2 = raw_file.replace('.tmp', '_part2.tmp')
            wf1 = open(tmp_fil1, mode="w")
            wf2 = open(tmp_fil2, mode="w")

            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)
            
            # 파일 내용을 라인별로 처리 (참조 사이트와 정확히 동일)
            for row in file_content.splitlines():
                rf1 = row[0:59]
                rf1_1 = rf1[0:1]
                rf1_2 = rf1[1:10]
                rf1_3 = rf1[10:22].strip()
                rf1_4 = rf1[22:59].strip()
                # 마지막 필드에 콤마가 포함될 수 있으므로 따옴표로 감싸기
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + ',"' + rf1_4 + '"' + '\n')
                rf2 = row[59:].lstrip()
                wf2.write(rf2 + '\n')

            wf1.close()
            wf2.close()

            part1_columns = ['product_type', 'short_code', 'standard_code', 'korean_name']
            df1 = self._read_csv_with_encoding(tmp_fil1, header=None, names=part1_columns)
    

            # df2 : 'ATM구분','행사가','기초자산 단축코드','기초자산 명'
            tmp_fil3 = raw_file.replace('.tmp', '_part3.tmp')
            wf3 = open(tmp_fil3, mode="w")

            # tmp_fil2 읽기 (참조 사이트와 동일하게 cp949 직접 사용)
            with open(tmp_fil2, mode="r", encoding="cp949") as f:
                for row in f:
                    rf2 = row[:]
                    rf2_1 = rf2[0:1]
                    rf2_2 = rf2[1:9]
                    rf2_3 = rf2[9:17]
                    rf2_4 = rf2[17:].strip()
                    wf3.write(rf2_1 + ',' + rf2_2 + ',' + rf2_3 + ',' + rf2_4 + '\n')

            wf3.close()

            part2_columns = ['atm_division', 'strike_price', 'underlying_short_code', 'underlying_name']
            df2 = self._read_csv_with_encoding(tmp_fil3, header=None, names=part2_columns)

            # DF : df1 + df2
            df = pd.concat([df1, df2], axis=1)

            # 임시 파일들 정리
            for tmp_file in [tmp_fil1, tmp_fil2, tmp_fil3]:
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)

            # DataFrame 직접 반환 (CSV 저장 제거됨)
            await ctx.info(f"국내EUREX연계 야간옵션 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_eurex_option_master", "process", str(e))
            await ctx.error(f"국내EUREX연계 야간옵션 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_overseas_future(self, raw_file: str, ctx) -> pd.DataFrame:
        """해외선물 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("해외선물 마스터파일 가공 중...")

        try:
            import pandas as pd

            # 원본 코드와 정확히 동일한 파싱
            columns = ['stock_code', 'server_auto_order_yn', 'server_auto_twap_yn', 'server_auto_economic_order_yn',
                       'filler', 'korean_name', 'exchange_code', 'item_code', 'item_type', 'output_decimal', 'calculation_decimal',
                       'tick_size', 'tick_value', 'contract_size', 'price_display_base', 'conversion_multiplier', 'most_active_month_yn',
                       'nearest_month_yn', 'spread_yn', 'spread_leg1_yn', 'sub_exchange_code']
            df = pd.DataFrame(columns=columns)
            ridx = 1

            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)
            
            # 파일 내용을 라인별로 처리
            for row in file_content.splitlines():
                a = row[:32]  # 종목코드
                b = row[32:33].rstrip()  # 서버자동주문 가능 종목 여부
                c = row[33:34].rstrip()  # 서버자동주문 TWAP 가능 종목 여부
                d = row[34:35]  # 서버자동 경제지표 주문 가능 종목 여부
                e = row[35:82].rstrip()  # 필러
                f = row[82:107].rstrip()  # 종목한글명
                g = row[-92:-82]  # 거래소코드 (ISAM KEY 1)
                h = row[-82:-72].rstrip()  # 품목코드 (ISAM KEY 2)
                i = row[-72:-69].rstrip()  # 품목종류
                j = row[-69:-64]  # 출력 소수점
                k = row[-64:-59].rstrip()  # 계산 소수점
                l = row[-59:-45].rstrip()  # 틱사이즈
                m = row[-45:-31]  # 틱가치
                n = row[-31:-21].rstrip()  # 계약크기
                o = row[-21:-17].rstrip()  # 가격표시진법
                p = row[-17:-7]  # 환산승수
                q = row[-7:-6].rstrip()  # 최다월물여부 0:원월물 1:최다월물
                r = row[-6:-5].rstrip()  # 최근월물여부 0:원월물 1:최근월물
                s = row[-5:-4].rstrip()  # 스프레드여부
                t = row[-4:-3].rstrip()  # 스프레드기준종목 LEG1 여부 Y/N
                u = row[-3:].rstrip()  # 서브 거래소 코드

                df.loc[ridx] = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u]
                ridx += 1

            # DataFrame 직접 반환 (CSV 저장 제거됨)

            await ctx.info(f"해외선물 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "overseas_future_master", "process", str(e))
            await ctx.error(f"해외선물 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_domestic_bond(self, raw_file: str, ctx) -> pd.DataFrame:
        """국내채권 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("국내채권 마스터파일 가공 중...")

        try:
            import pandas as pd

            # 원본 코드와 정확히 동일한 파싱
            await ctx.info("고정폭 텍스트 파일 파싱 중...")
            
            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)
            lines = file_content.splitlines()

            data = []
            for row in lines:
                row = row.strip()
                bond_type = row[0:2].strip()
                bond_cls_code = row[2:4].strip()
                stnd_iscd = row[4:16].strip()
                rdmp_date = row[-8:].strip()
                pblc_date = row[-16:-8].strip()
                lstn_date = row[-24:-16].strip()
                bond_int_cls_code = row[-26:-24].strip()
                sname = row[16:-26].rstrip()  # 종목명을 뒤에서부터 추출하여 남은 부분

                data.append(
                    [bond_type, bond_cls_code, stnd_iscd, sname, bond_int_cls_code, lstn_date, pblc_date, rdmp_date])

            columns = ['bond_type', 'bond_classification_code', 'standard_code', 'bond_name', 'bond_interest_classification_code', 'listing_date', 'issue_date', 'redemption_date']
            
            # 공통 DataFrame 처리
            df = self._create_dataframe(data, columns)

            await ctx.info(f"국내채권 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "domestic_bond_master", "process", str(e))
            await ctx.error(f"국내채권 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()

    async def __process_elw(self, raw_file: str, ctx) -> pd.DataFrame:
        """ELW 마스터파일 가공 (원본 코드와 동일)"""
        await ctx.info("ELW 마스터파일 가공 중...")

        try:
            import pandas as pd

            # 원본 코드와 정확히 동일한 파싱
            await ctx.info("복잡한 고정폭 텍스트 파일 파싱 중...")
            
            # 파일 읽기 (공통 로직)
            file_content = await self._read_file_with_encoding(raw_file, ctx)
            lines = file_content.splitlines()

            data = []
            for row in lines:
                # print(row)
                mksc_shrn_iscd = row[0:9].strip()  # 단축코드
                stnd_iscd = row[9:21].strip()  # 표준코드
                hts_kor_isnm = row[21:50].strip()  # 한글 종목명

                crow = row[50:].strip()
                elw_nvlt_optn_cls_code = crow[:1].strip()  # ELW권리형태
                elw_ko_barrier = crow[1:14].strip()  # ELW조기종료발생기준가격
                bskt_yn = crow[14:15].strip()  # 바스켓 여부 (Y/N)
                unas_iscd1 = crow[15:24].strip()  # 기초자산코드1
                unas_iscd2 = crow[24:33].strip()  # 기초자산코드2
                unas_iscd3 = crow[33:42].strip()  # 기초자산코드3
                unas_iscd4 = crow[42:51].strip()  # 기초자산코드4
                unas_iscd5 = crow[51:60].strip()  # 기초자산코드5

                # Calculate positions from the end of the row
                mrkt_prtt_no10 = row[-6:].strip()  # 시장 참가자 번호10
                mrkt_prtt_no9 = row[-11:-6].strip()  # 시장 참가자 번호9
                mrkt_prtt_no8 = row[-16:-11].strip()  # 시장 참가자 번호8
                mrkt_prtt_no7 = row[-21:-16].strip()  # 시장 참가자 번호7
                mrkt_prtt_no6 = row[-26:-21].strip()  # 시장 참가자 번호6
                mrkt_prtt_no5 = row[-31:-26].strip()  # 시장 참가자 번호5
                mrkt_prtt_no4 = row[-36:-31].strip()  # 시장 참가자 번호4
                mrkt_prtt_no3 = row[-41:-36].strip()  # 시장 참가자 번호3
                mrkt_prtt_no2 = row[-46:-41].strip()  # 시장 참가자 번호2
                mrkt_prtt_no1 = row[-51:-46].strip()  # 시장 참가자 번호1
                lstn_stcn = row[-66:-51].strip()  # 상장주수(천)
                prdy_avls = row[-75:-66].strip()  # 전일시가총액(억)
                paym_date = row[-83:-75].strip()  # 지급일
                rght_type_cls_code = row[-84:-83].strip()  # 권리 유형 구분 코드
                rmnn_dynu = row[-88:-84].strip()  # 잔존 일수
                stck_last_tr_month = row[-96:-88].strip()  # 최종거래일
                acpr = row[-105:-96].strip()  # 행사가
                elw_pblc_mrkt_prtt_no = row[-110:-105].strip()  # 발행사코드

                elw_pblc_istu_name = row[-11:-110].strip()  # 발행사 한글 종목명

                data.append([mksc_shrn_iscd, stnd_iscd, hts_kor_isnm,
                             elw_nvlt_optn_cls_code, elw_ko_barrier, bskt_yn,
                             unas_iscd1, unas_iscd2, unas_iscd3, unas_iscd4,
                             unas_iscd5, elw_pblc_istu_name, elw_pblc_mrkt_prtt_no,
                             acpr, stck_last_tr_month, rmnn_dynu, rght_type_cls_code,
                             paym_date, prdy_avls, lstn_stcn, mrkt_prtt_no1,
                             mrkt_prtt_no2, mrkt_prtt_no3, mrkt_prtt_no4,
                             mrkt_prtt_no5, mrkt_prtt_no6, mrkt_prtt_no7,
                             mrkt_prtt_no8, mrkt_prtt_no9, mrkt_prtt_no10])

            columns = ['short_code', 'standard_code', 'korean_name', 'elw_right_type', 'elw_early_termination_price',
                       'basket_yn', 'underlying_code1', 'underlying_code2', 'underlying_code3',
                       'underlying_code4', 'underlying_code5', 'issuer_korean_name', 'issuer_code',
                       'strike_price', 'last_trading_date', 'remaining_days', 'right_type_division_code', 'payment_date',
                       'prev_day_market_cap_billion', 'listed_shares_thousand', 'market_participant_no1',
                       'market_participant_no2', 'market_participant_no3', 'market_participant_no4',
                       'market_participant_no5', 'market_participant_no6', 'market_participant_no7',
                       'market_participant_no8', 'market_participant_no9', 'market_participant_no10']

            # 공통 DataFrame 처리
            df = self._create_dataframe(data, columns)

            await ctx.info(f"ELW 마스터파일 가공 완료: {len(df)}개 종목")
            return df

        except Exception as e:
            self._log("error", "elw_master", "process", str(e))
            await ctx.error(f"ELW 마스터파일 가공 실패: {str(e)}")
            return pd.DataFrame()
    
    