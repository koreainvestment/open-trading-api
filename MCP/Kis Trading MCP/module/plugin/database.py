from typing import Any, Dict, List, Optional, Type, Union
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseEngine:
    """1 SQLite 파일 : 1 엔진을 관리하는 클래스"""
    
    def __init__(self, db_path: str, models: List[Type]):
        """
        Args:
            db_path: SQLite 파일 경로
            models: 해당 데이터베이스에 포함될 모델 클래스들의 리스트
        """
        self.db_path = db_path
        self.models = models
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """데이터베이스 엔진 초기화"""
        try:
            # SQLite 연결 문자열 생성
            db_url = f"sqlite:///{self.db_path}"
            
            # 엔진 생성
            self.engine = create_engine(
                db_url,
                echo=False,  # SQL 로그 출력 여부
                pool_pre_ping=True,  # 연결 상태 확인
                connect_args={"check_same_thread": False}  # SQLite 멀티스레드 지원
            )
            
            # 세션 팩토리 생성
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 테이블 생성
            self._create_tables()
            
            logger.info(f"Database engine initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine {self.db_path}: {e}")
            raise
    
    def _create_tables(self):
        """모든 모델의 테이블 생성"""
        try:
            from model.base import Base
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"Tables created for {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to create tables for {self.db_path}: {e}")
            raise
    
    def get_session(self) -> Session:
        """새로운 데이터베이스 세션 반환"""
        if not self.SessionLocal:
            raise RuntimeError("Database engine not initialized")
        return self.SessionLocal()
    
    def insert(self, model_instance: Any) -> Any:
        """
        모델 인스턴스를 데이터베이스에 삽입
        
        Args:
            model_instance: 삽입할 모델 인스턴스
            
        Returns:
            삽입된 모델 인스턴스 (ID 포함)
        """
        session = self.get_session()
        try:
            session.add(model_instance)
            session.commit()
            session.refresh(model_instance)
            logger.info(f"Inserted record: {type(model_instance).__name__}")
            return model_instance
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to insert record: {e}")
            raise
        finally:
            session.close()
    
    def update(self, model_class: Type, record_id: int, update_data: Dict[str, Any]) -> Optional[Any]:
        """
        ID로 레코드 업데이트
        
        Args:
            model_class: 업데이트할 모델 클래스
            record_id: 업데이트할 레코드의 ID
            update_data: 업데이트할 필드와 값의 딕셔너리
            
        Returns:
            업데이트된 모델 인스턴스 또는 None
        """
        session = self.get_session()
        try:
            # 레코드 조회
            record = session.query(model_class).filter(model_class.id == record_id).first()
            if not record:
                logger.warning(f"Record not found: {model_class.__name__} ID {record_id}")
                return None
            
            # 필드 업데이트
            for field, value in update_data.items():
                if hasattr(record, field):
                    setattr(record, field, value)
                else:
                    logger.warning(f"Field '{field}' not found in {model_class.__name__}")
            
            session.commit()
            session.refresh(record)
            logger.info(f"Updated record: {model_class.__name__} ID {record_id}")
            return record
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update record: {e}")
            raise
        finally:
            session.close()
    
    def delete(self, model_class: Type, record_id: int) -> bool:
        """
        ID로 레코드 삭제
        
        Args:
            model_class: 삭제할 모델 클래스
            record_id: 삭제할 레코드의 ID
            
        Returns:
            삭제 성공 여부
        """
        session = self.get_session()
        try:
            # 레코드 조회
            record = session.query(model_class).filter(model_class.id == record_id).first()
            if not record:
                logger.warning(f"Record not found: {model_class.__name__} ID {record_id}")
                return False
            
            session.delete(record)
            session.commit()
            logger.info(f"Deleted record: {model_class.__name__} ID {record_id}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to delete record: {e}")
            raise
        finally:
            session.close()
    
    def list(self, model_class: Type, filters: Optional[Dict[str, Any]] = None, 
             limit: Optional[int] = None, offset: Optional[int] = None) -> List[Any]:
        """
        조건에 맞는 레코드 목록 조회
        
        Args:
            model_class: 조회할 모델 클래스
            filters: 필터 조건 딕셔너리 {field: value}
            limit: 조회할 최대 개수
            offset: 건너뛸 개수
            
        Returns:
            조회된 레코드 리스트
        """
        session = self.get_session()
        try:
            query = session.query(model_class)
            
            # 필터 적용
            if filters:
                for field, value in filters.items():
                    if hasattr(model_class, field):
                        query = query.filter(getattr(model_class, field) == value)
                    else:
                        logger.warning(f"Field '{field}' not found in {model_class.__name__}")
            
            # 페이징 적용
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            logger.info(f"Listed {len(results)} records: {model_class.__name__}")
            return results
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to list records: {e}")
            raise
        finally:
            session.close()
    
    def get(self, model_class: Type, filters: Dict[str, Any]) -> Optional[Any]:
        """
        조건에 맞는 첫 번째 레코드 조회
        
        Args:
            model_class: 조회할 모델 클래스
            filters: 필터 조건 딕셔너리 {field: value}
            
        Returns:
            조회된 레코드 또는 None
        """
        session = self.get_session()
        try:
            query = session.query(model_class)
            
            # 필터 적용
            for field, value in filters.items():
                if hasattr(model_class, field):
                    query = query.filter(getattr(model_class, field) == value)
                else:
                    logger.warning(f"Field '{field}' not found in {model_class.__name__}")
            
            result = query.first()
            if result:
                logger.info(f"Found record: {model_class.__name__}")
            else:
                logger.info(f"No record found: {model_class.__name__}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get record: {e}")
            raise
        finally:
            session.close()
    
    def count(self, model_class: Type, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        조건에 맞는 레코드 개수 조회
        
        Args:
            model_class: 조회할 모델 클래스
            filters: 필터 조건 딕셔너리 {field: value}
            
        Returns:
            레코드 개수
        """
        session = self.get_session()
        try:
            query = session.query(model_class)
            
            # 필터 적용
            if filters:
                for field, value in filters.items():
                    if hasattr(model_class, field):
                        query = query.filter(getattr(model_class, field) == value)
                    else:
                        logger.warning(f"Field '{field}' not found in {model_class.__name__}")
            
            count = query.count()
            logger.info(f"Counted {count} records: {model_class.__name__}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to count records: {e}")
            raise
        finally:
            session.close()
    
    def bulk_replace_master_data(self, model_class: Type, data_list: List[Dict], master_name: str) -> int:
        """
        마스터 데이터 추가 (INSERT만) - 카테고리 레벨에서 이미 삭제됨
        
        Args:
            model_class: 마스터 데이터 모델 클래스
            data_list: 삽입할 데이터 리스트 (딕셔너리 리스트)
            master_name: 마스터파일명 (로깅용)
            
        Returns:
            삽입된 레코드 수
        """
        session = self.get_session()
        try:
            # 새 데이터 배치 삽입 (카테고리 레벨에서 이미 삭제되었으므로 INSERT만)
            if data_list:
                # 배치 크기 설정 (메모리 효율성을 위해 1000개씩)
                batch_size = 1000
                total_inserted = 0
                
                for i in range(0, len(data_list), batch_size):
                    batch = data_list[i:i + batch_size]
                    batch_objects = []
                    
                    for data in batch:
                        # 모든 값을 문자열로 강제 변환 (SQLAlchemy 타입 추론 방지)
                        str_data = {key: str(value) if value is not None else None for key, value in data.items()}
                        
                        # 딕셔너리를 모델 인스턴스로 변환
                        obj = model_class(**str_data)
                        batch_objects.append(obj)
                    
                    # 배치 삽입
                    session.bulk_save_objects(batch_objects)
                    total_inserted += len(batch_objects)
                    
                    # 중간 커밋 (메모리 절약)
                    if i + batch_size < len(data_list):
                        session.commit()
                        logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch_objects)} records")
                
                # 최종 커밋
                session.commit()
                logger.info(f"Bulk replace completed: {total_inserted} records inserted into {model_class.__name__}")
                return total_inserted
            else:
                logger.warning(f"No data to insert for {master_name}")
                return 0
                
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to bulk replace master data for {master_name}: {e}")
            raise
        finally:
            session.close()
    
    def update_master_timestamp(self, tool_name: str, record_count: int = None) -> bool:
        """
        마스터파일 업데이트 시간 기록
        
        Args:
            tool_name: 툴명 (예: domestic_stock, overseas_stock)
            record_count: 레코드 수 (선택사항)
            
        Returns:
            업데이트 성공 여부
        """
        from model.updated import Updated
        
        session = self.get_session()
        try:
            # 기존 레코드 조회
            existing_record = session.query(Updated).filter(Updated.tool_name == tool_name).first()
            
            if existing_record:
                # 기존 레코드 업데이트
                existing_record.updated_at = datetime.now()
                logger.info(f"Updated timestamp for {tool_name}")
            else:
                # 새 레코드 생성
                new_record = Updated(
                    tool_name=tool_name,
                    updated_at=datetime.now()
                )
                session.add(new_record)
                logger.info(f"Created new timestamp record for {tool_name}")
            
            session.commit()
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update master timestamp for {tool_name}: {e}")
            return False
        finally:
            session.close()
    
    def get_master_update_time(self, tool_name: str) -> Optional[datetime]:
        """
        마스터파일 마지막 업데이트 시간 조회
        
        Args:
            tool_name: 툴명 (예: domestic_stock, overseas_stock)
            
        Returns:
            마지막 업데이트 시간 또는 None
        """
        from model.updated import Updated
        
        session = self.get_session()
        try:
            record = session.query(Updated).filter(Updated.tool_name == tool_name).first()
            if record:
                logger.info(f"Found update time for {tool_name}: {record.updated_at}")
                return record.updated_at
            else:
                logger.info(f"No update record found for {tool_name}")
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to get master update time for {tool_name}: {e}")
            return None
        finally:
            session.close()
    
    def is_master_data_available(self, model_class: Type) -> bool:
        """
        마스터 데이터 존재 여부 확인
        
        Args:
            model_class: 마스터 데이터 모델 클래스
            
        Returns:
            데이터 존재 여부
        """
        session = self.get_session()
        try:
            count = session.query(model_class).count()
            available = count > 0
            logger.info(f"Master data availability check for {model_class.__name__}: {available} ({count} records)")
            return available
        except SQLAlchemyError as e:
            logger.error(f"Failed to check master data availability for {model_class.__name__}: {e}")
            return False
        finally:
            session.close()

    def close(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()
            logger.info(f"Database engine closed: {self.db_path}")
    
    def __repr__(self):
        return f"DatabaseEngine(db_path='{self.db_path}', models={len(self.models)})"


class Database:
    """데이터베이스 엔진들을 관리하는 Singleton 클래스"""
    
    _instance: Optional['Database'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Database':
        """Singleton 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """초기화 (한 번만 실행)"""
        if not self._initialized:
            self.dbs: Dict[str, DatabaseEngine] = {}
            self._initialized = True
            logger.info("Database singleton instance created")
    
    def new(self, db_dir: str = "configs/master") -> None:
        """
        마스터 데이터베이스 엔진 초기화
        
        Args:
            db_dir: 데이터베이스 파일이 저장될 디렉토리
        """
        try:
            # 데이터베이스 디렉토리 생성
            os.makedirs(db_dir, exist_ok=True)
            
            # 하나의 통합 마스터 데이터베이스 엔진 생성
            self._create_master_engine(db_dir)
            
            logger.info(f"Master database engine initialized: '{db_dir}/master.db'")
            logger.info(f"Available databases: {list(self.dbs.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize master database: {e}")
            raise
    
    def _create_master_engine(self, db_dir: str):
        """통합 마스터 데이터베이스 엔진 생성"""
        from model import ALL_MODELS
        
        db_path = os.path.join(db_dir, "master.db")
        
        self.dbs["master"] = DatabaseEngine(db_path, ALL_MODELS)
        logger.info("Created master database engine with all models")
    
    def get_by_name(self, name: str) -> DatabaseEngine:
        """
        이름으로 데이터베이스 엔진 조회
        
        Args:
            name: 데이터베이스 이름
            
        Returns:
            DatabaseEngine 인스턴스
            
        Raises:
            KeyError: 해당 이름의 데이터베이스가 없는 경우
        """
        if name not in self.dbs:
            available_dbs = list(self.dbs.keys())
            raise KeyError(f"Database '{name}' not found. Available databases: {available_dbs}")
        
        return self.dbs[name]
    
    def get_available_databases(self) -> List[str]:
        """사용 가능한 데이터베이스 이름 목록 반환"""
        return list(self.dbs.keys())
    
    def is_initialized(self) -> bool:
        """데이터베이스가 초기화되었는지 확인"""
        return len(self.dbs) > 0
    
    def ensure_initialized(self, db_dir: str = "configs/master") -> bool:
        """데이터베이스가 초기화되지 않은 경우에만 초기화"""
        if not self.is_initialized():
            try:
                self.new(db_dir)
                logger.info("Database initialized on demand")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize database on demand: {e}")
                return False
        return True
    
    def close_all(self):
        """모든 데이터베이스 연결 종료"""
        for name, engine in self.dbs.items():
            try:
                engine.close()
                logger.info(f"Closed database: {name}")
            except Exception as e:
                logger.error(f"Failed to close database {name}: {e}")
        
        self.dbs.clear()
        logger.info("All database connections closed")
    
    def __repr__(self):
        return f"Database(engines={len(self.dbs)}, names={list(self.dbs.keys())})"
    
    def __del__(self):
        """소멸자 - 모든 연결 정리"""
        if hasattr(self, 'dbs') and self.dbs:
            self.close_all()
