"""Lean 프로젝트 관리자

Lean 워크스페이스와 프로젝트 디렉토리 구조를 관리.
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Lean 워크스페이스 기본 경로
DEFAULT_WORKSPACE = Path(".lean-workspace")


@dataclass
class LeanProject:
    """Lean 프로젝트 정보"""
    run_id: str
    project_dir: Path
    data_dir: Path
    symbols: List[str]
    start_date: str
    end_date: str
    initial_capital: float
    commission_rate: float = 0.00015  # 0.015%
    tax_rate: float = 0.0023  # 0.23% (매도시)
    market_type: str = "krx"  # "krx" | "us"
    currency: str = "KRW"  # "KRW" | "USD"
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def main_py(self) -> Path:
        return self.project_dir / "main.py"
    
    @property
    def config_json(self) -> Path:
        return self.project_dir / "config.json"
    
    @property
    def output_dir(self) -> Path:
        return self.project_dir / "backtests"


class LeanProjectManager:
    """Lean 프로젝트 관리자"""

    _RUN_ID_PREFIX_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$")
    
    workspace: Path = DEFAULT_WORKSPACE
    
    @classmethod
    def set_workspace(cls, path: str) -> None:
        """워크스페이스 경로 설정"""
        cls.workspace = Path(path)

    @classmethod
    def generate_run_id(cls, prefix: str = "bt") -> str:
        """사용자 입력과 무관한 내부 실행 ID를 생성한다."""
        if not cls._RUN_ID_PREFIX_PATTERN.fullmatch(prefix):
            raise ValueError("Invalid run ID prefix")
        return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:12]}"

    @staticmethod
    def _validate_run_id(run_id: str) -> None:
        """과거의 안전한 표시 문자는 허용하되 경로 의미를 갖는 값은 거부한다."""
        if not isinstance(run_id, str) or not 1 <= len(run_id) <= 255:
            raise ValueError("Invalid run ID")
        if run_id in {".", ".."} or "/" in run_id or "\\" in run_id or ":" in run_id:
            raise ValueError("Invalid run ID")
        if any(ord(char) < 32 or ord(char) == 127 for char in run_id):
            raise ValueError("Invalid run ID")
        if Path(run_id).is_absolute() or Path(run_id).name != run_id:
            raise ValueError("Invalid run ID")

    @classmethod
    def _projects_root(cls, create: bool = False) -> Path:
        workspace_root = cls.workspace.resolve()
        if create:
            workspace_root.mkdir(parents=True, exist_ok=True)
        root = workspace_root / "projects"
        if root.is_symlink():
            raise ValueError("Symbolic-link projects root is not allowed")
        if create:
            root.mkdir(exist_ok=True)
        resolved = root.resolve()
        if resolved.parent != workspace_root:
            raise ValueError("Projects root escapes workspace")
        return resolved

    @classmethod
    def _project_path(cls, run_id: str, *, create_root: bool = False) -> Path:
        """검증된 단일 경로 요소를 projects root 아래 경로로 변환한다."""
        cls._validate_run_id(run_id)

        root = cls._projects_root(create=create_root)
        candidate = root / run_id
        resolved = candidate.resolve(strict=False)
        if resolved.parent != root:
            raise ValueError("Project path escapes projects root")
        if candidate.is_symlink():
            raise ValueError("Symbolic-link projects are not allowed")
        return candidate
    
    @classmethod
    def init_workspace(cls) -> Path:
        """워크스페이스 초기화"""
        ws = cls.workspace
        ws.mkdir(parents=True, exist_ok=True)
        
        # lean.json 생성
        lean_json = ws / "lean.json"
        if not lean_json.exists():
            config = {
                "data-folder": str(ws / "data"),
                "results-destination-folder": str(ws / "results"),
                "engine-type": "local",
            }
            lean_json.write_text(json.dumps(config, indent=2))
        
        # data 디렉토리 생성
        data_dir = ws / "data" / "equity" / "krx" / "daily"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # projects 디렉토리 생성
        cls._projects_root(create=True)
        
        logger.info(f"[Lean] 워크스페이스 초기화: {ws}")
        return ws
    
    @classmethod
    def create_project(
        cls,
        run_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float,
        commission_rate: float = 0.00015,
        tax_rate: float = 0.0023,
        strategy_type: str = "unknown",
        strategy_params: Optional[dict] = None,
        strategy_id: Optional[str] = None,
        strategy_name: Optional[str] = None,
        market_type: str = "krx",
        currency: str = "KRW",
    ) -> LeanProject:
        """새 프로젝트 생성"""
        # 워크스페이스 초기화
        ws = cls.init_workspace()
        
        # 프로젝트 디렉토리 생성
        project_dir = cls._project_path(run_id, create_root=True)
        if os.path.lexists(project_dir):
            raise FileExistsError(f"Project already exists: {run_id}")
        project_dir.mkdir()
        if project_dir.resolve().parent != cls._projects_root():
            raise ValueError("Project path escapes projects root")
        
        # 데이터 디렉토리 (마켓별 분리)
        # krx: /data/equity/krx/daily/
        # us: /data/equity/usa/daily/
        market_folder = "krx" if market_type == "krx" else "usa"
        data_dir = ws / "data" / "equity" / market_folder / "daily"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # config.json 생성 (strategy 정보 포함)
        config = {
            "algorithm-language": "Python",
            "strategy_type": strategy_type,
            "strategy_params": strategy_params or {},
            "strategy_id": strategy_id,
            "strategy_name": strategy_name,
            "market_type": market_type,
            "currency": currency,
            "parameters": {
                "symbols": ",".join(symbols),
                "start_date": start_date,
                "end_date": end_date,
                "initial_capital": str(int(initial_capital)),
                "commission_rate": str(commission_rate),
                "tax_rate": str(tax_rate),
            },
        }
        
        config_path = project_dir / "config.json"
        config_path.write_text(json.dumps(config, indent=2))
        
        # backtests 디렉토리 생성
        (project_dir / "backtests").mkdir(exist_ok=True)
        
        project = LeanProject(
            run_id=run_id,
            project_dir=project_dir,
            data_dir=data_dir,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            tax_rate=tax_rate,
            market_type=market_type,
            currency=currency,
        )
        
        logger.info(f"[Lean] 프로젝트 생성: {run_id} (market: {market_type})")
        return project
    
    @classmethod
    def get_project(cls, run_id: str) -> Optional[LeanProject]:
        """기존 프로젝트 조회"""
        project_dir = cls._project_path(run_id)
        
        if not project_dir.exists():
            return None
        
        config_path = project_dir / "config.json"
        if not config_path.exists():
            return None
        
        config = json.loads(config_path.read_text())
        params = config.get("parameters", {})
        
        # 마켓/통화 정보 (기존 프로젝트 호환)
        market_type = config.get("market_type", "krx")
        currency = config.get("currency", "KRW")
        market_folder = "krx" if market_type == "krx" else "usa"
        
        return LeanProject(
            run_id=run_id,
            project_dir=project_dir,
            data_dir=cls.workspace / "data" / "equity" / market_folder / "daily",
            symbols=params.get("symbols", "").split(","),
            start_date=params.get("start_date", ""),
            end_date=params.get("end_date", ""),
            initial_capital=float(params.get("initial_capital", 100000000)),
            market_type=market_type,
            currency=currency,
        )
    
    @classmethod
    def list_projects(cls) -> List[str]:
        """모든 프로젝트 목록"""
        projects_dir = cls._projects_root()
        if not projects_dir.exists():
            return []
        
        return [p.name for p in projects_dir.iterdir() if p.is_dir() and not p.is_symlink()]
    
    @classmethod
    def cleanup_project(cls, run_id: str) -> bool:
        """프로젝트 삭제"""
        import shutil
        
        project_dir = cls._project_path(run_id)
        
        if project_dir.exists():
            shutil.rmtree(project_dir)
            logger.info(f"[Lean] 프로젝트 삭제: {run_id}")
            return True
        
        return False
    
    @classmethod
    def list_projects_with_results(cls, limit: int = 20) -> List[dict]:
        """결과가 있는 프로젝트 목록 조회 (히스토리용)
        
        Returns:
            최근 실행 목록 (run_id, 전략, 종목, 날짜, 통계 요약)
        """
        projects_dir = cls._projects_root()
        if not projects_dir.exists():
            return []
        
        results = []
        
        # 프로젝트 디렉토리 목록 (수정 시간 역순)
        project_dirs = sorted(
            [p for p in projects_dir.iterdir() if p.is_dir() and not p.is_symlink()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:limit]
        
        for project_dir in project_dirs:
            run_id = project_dir.name
            config_path = project_dir / "config.json"
            
            if not config_path.exists():
                continue
            
            # 결과 파일이 있는지 확인 (없으면 히스토리에서 제외)
            backtests_dir = project_dir / "backtests"
            has_result = (
                (backtests_dir / "Algorithm.json").exists() or
                any(backtests_dir.glob("*/Algorithm.json")) if backtests_dir.exists() else False
            )
            if not has_result:
                continue
            
            try:
                config = json.loads(config_path.read_text())
                params = config.get("parameters", {})
                
                # 전략 타입 (config에 없으면 main.py에서 추론)
                strategy_type = config.get("strategy_type")
                if not strategy_type or strategy_type == "unknown":
                    strategy_type = cls._infer_strategy_type(project_dir)
                
                # 사용자 정의 이름 (저장된 경우)
                display_name = config.get("display_name", "")
                
                # 통계 추출 (Algorithm-summary.json 우선)
                summary = cls._extract_summary(project_dir / "backtests")
                
                results.append({
                    "run_id": run_id,
                    "created_at": datetime.fromtimestamp(project_dir.stat().st_mtime).isoformat(),
                    "strategy_type": strategy_type,
                    "strategy_id": config.get("strategy_id"),  # 커스텀 전략 ID
                    "strategy_name": config.get("strategy_name"),  # 커스텀 전략 이름
                    "display_name": display_name,
                    "symbols": params.get("symbols", "").split(",") if params.get("symbols") else [],
                    "start_date": params.get("start_date", ""),
                    "end_date": params.get("end_date", ""),
                    "market_type": config.get("market_type", "krx"),
                    "currency": config.get("currency", "KRW"),
                    "summary": summary,
                })
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"[Lean] 프로젝트 파싱 실패: {run_id} - {e}")
                continue
        
        return results
    
    @classmethod
    def _infer_strategy_type(cls, project_dir: Path) -> str:
        """main.py에서 전략 타입 추론"""
        main_py = project_dir / "main.py"
        if not main_py.exists():
            return "unknown"
        
        try:
            content = main_py.read_text()
            
            # 전략 패턴 매칭
            patterns = {
                "sma_crossover": ["SMA", "short_sma", "long_sma", "crossover"],
                "rsi": ["RSI", "rsi_indicator", "oversold", "overbought"],
                "macd": ["MACD", "macd_indicator", "Signal"],
                "bollinger": ["BollingerBands", "BB", "upper_band", "lower_band"],
                "momentum": ["MOMP", "momentum_indicator"],
                "breakout_high": ["MAX", "highest", "breakout"],
                "consecutive": ["consecutive", "up_days", "down_days"],
                "ma_divergence": ["divergence", "deviation"],
                "volatility_breakout": ["volatility", "ATR"],
                "mean_reversion": ["reversion", "mean"],
            }
            
            for strategy, keywords in patterns.items():
                if any(kw in content for kw in keywords):
                    return strategy
            
            return "custom"
        except (OSError, UnicodeDecodeError):
            # 파일 읽기 실패(권한/삭제 경합) 또는 비 UTF-8 인코딩
            return "unknown"
    
    @classmethod
    def _extract_summary(cls, backtests_dir: Path) -> dict:
        """백테스트 결과에서 통계 요약 추출"""
        summary = {
            "total_return_pct": 0,
            "sharpe_ratio": 0,
            "max_drawdown_pct": 0,
            "num_trades": 0,
        }
        
        if not backtests_dir.exists():
            return summary
        
        # Algorithm-summary.json 우선 (더 정확한 통계)
        summary_file = backtests_dir / "Algorithm-summary.json"
        if summary_file.exists():
            try:
                data = json.loads(summary_file.read_text())
                stats = data.get("statistics", {})
                
                # Net Profit 파싱 (예: "16.985%")
                net_profit = stats.get("Net Profit", "0%")
                summary["total_return_pct"] = cls._parse_percent(net_profit)
                
                # Sharpe Ratio 파싱 (예: "0.388")
                sharpe = stats.get("Sharpe Ratio", "0")
                summary["sharpe_ratio"] = cls._parse_float(sharpe)
                
                # Drawdown 파싱 (예: "15.900%")
                drawdown = stats.get("Drawdown", "0%")
                summary["max_drawdown_pct"] = cls._parse_percent(drawdown)
                
                # Total Orders 파싱 (예: "88")
                orders = stats.get("Total Orders", "0")
                summary["num_trades"] = int(cls._parse_float(orders))
                
                return summary
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[Lean] summary 파싱 실패: {e}")
        
        # Algorithm.json 폴백
        result_file = backtests_dir / "Algorithm.json"
        if result_file.exists():
            try:
                data = json.loads(result_file.read_text())
                # rollingWindow에서 마지막 portfolioStatistics 사용
                rolling = data.get("rollingWindow", {})
                if rolling:
                    last_key = list(rolling.keys())[-1] if rolling else None
                    if last_key:
                        portfolio_stats = rolling[last_key].get("portfolioStatistics", {})
                        summary["total_return_pct"] = cls._parse_float(portfolio_stats.get("totalNetProfit", 0)) * 100
                        summary["sharpe_ratio"] = cls._parse_float(portfolio_stats.get("sharpeRatio", 0))
                        summary["max_drawdown_pct"] = cls._parse_float(portfolio_stats.get("drawdown", 0)) * 100
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[Lean] result 파싱 실패: {e}")
        
        return summary
    
    @classmethod
    def _parse_percent(cls, value: str) -> float:
        """퍼센트 문자열 파싱 (예: "16.985%" → 16.985)"""
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).replace("%", "").replace(",", "").strip())
        except ValueError:
            return 0.0
    
    @classmethod
    def _parse_float(cls, value) -> float:
        """숫자 문자열 파싱"""
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).replace("$", "").replace(",", "").strip())
        except ValueError:
            return 0.0
    
    @classmethod
    def update_project_name(cls, run_id: str, display_name: str) -> bool:
        """프로젝트 이름 수정"""
        project_dir = cls._project_path(run_id)
        config_path = project_dir / "config.json"
        
        if not config_path.exists():
            return False
        
        try:
            config = json.loads(config_path.read_text())
            config["display_name"] = display_name
            config_path.write_text(json.dumps(config, indent=2))
            logger.info(f"[Lean] 프로젝트 이름 변경: {run_id} → {display_name}")
            return True
        except (OSError, ValueError, TypeError) as e:
            # OSError: 읽기/쓰기 실패, ValueError: JSONDecodeError/UnicodeDecodeError,
            # TypeError: config.json 최상위가 dict 가 아닌 경우
            logger.error(f"[Lean] 이름 변경 실패: {run_id} - {e}")
            return False
    
    @classmethod
    def get_project_result(cls, run_id: str) -> Optional[dict]:
        """프로젝트 결과 조회 (API 응답 형식)
        
        Returns:
            기존 RunCacheService와 동일한 형식의 결과
        """
        from .executor import LeanRun
        from .result_formatter import ResultFormatter
        
        project = cls.get_project(run_id)
        if not project:
            return None
        
        # 결과 디렉토리 확인
        output_dir = project.project_dir / "backtests"
        if not output_dir.exists():
            return None
        
        # LeanRun 객체 생성 (결과 로드용)
        run = LeanRun(
            project=project,
            success=True,
            output_dir=output_dir,
        )
        
        # 결과 로드
        raw_result = run.load_result()
        if not raw_result:
            return None
        
        # API 응답 형식으로 변환
        config_path = project.project_dir / "config.json"
        strategy_type = "unknown"
        strategy_params = {}
        strategy_id = None
        strategy_name = None
        
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
                strategy_type = config.get("strategy_type", "unknown")
                strategy_params = config.get("strategy_params", {})
                strategy_id = config.get("strategy_id")
                strategy_name = config.get("strategy_name")
            except json.JSONDecodeError:
                pass
        
        # ResultFormatter 결과 (전체 API 응답)
        formatted_result = ResultFormatter.to_api_response(
            run=run,
            symbols=project.symbols,
            start_date=project.start_date,
            end_date=project.end_date,
            initial_capital=project.initial_capital,
            strategy_type=strategy_type,
            strategy_params=strategy_params,
            currency=project.currency,
        )
        
        # 기존 RunCacheService 형식과 호환되는 응답
        return {
            "run_id": run_id,
            "created_at": datetime.fromtimestamp(project.project_dir.stat().st_mtime).isoformat(),
            "market_type": project.market_type,
            "currency": project.currency,
            "request": {
                "symbols": project.symbols,
                "strategy_type": strategy_type,
                "strategy_params": strategy_params,
                "strategy_id": strategy_id,
                "strategy_name": strategy_name,
                "start_date": project.start_date,
                "end_date": project.end_date,
                "initial_capital": project.initial_capital,
            },
            # result 키 아래에 전체 formatted_result를 넣음 (UI 호환)
            "result": formatted_result,
        }
    
    @classmethod
    def cleanup_all_projects(cls) -> int:
        """모든 프로젝트 삭제
        
        Returns:
            삭제된 프로젝트 수
        """
        import shutil
        
        projects_dir = cls._projects_root()
        if not projects_dir.exists():
            return 0
        
        count = 0
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir() and not project_dir.is_symlink():
                shutil.rmtree(project_dir)
                count += 1
        
        logger.info(f"[Lean] 전체 프로젝트 삭제: {count}개")
        return count
