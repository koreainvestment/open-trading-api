"""
전략 실행기

4가지 실행 경로를 통합:
1. preset (class 있음) - 직접 인스턴스화
2. builder-only (class 없음, builder_state 있음) - DSL 변환 → 코드 생성 → 동적 실행
3. local_ (프런트에서 저장한 전략) - builder_state로 동적 실행
4. custom: (사용자 .py 파일) - 파일 동적 로드

모든 경로는 (code, name) → Signal → SignalResult로 변환되며,
결과를 log 콜백에 기록합니다.
"""

import importlib.util
import os
import tempfile
from typing import Any, Callable, Dict, List

from core.errors import BOUNDARY_ERRORS
from strategy_core.dsl.converter import builder_state_to_dsl
from strategy_core.dsl.parser import parse_strategy
from strategy_core.dsl.codegen import StrategyCodeGenerator
from strategy_core.name_utils import sanitize_strategy_name
from strategy_core.storage import get_generated_strategy_file


def execute_with_class(
    strategy_class,
    param_map: Dict[str, str],
    params: Dict[str, Any],
    stocks: List[str],
    strategy_id: str,
    log: Callable,
    get_stock_name: Callable,
    api_sleep: Callable,
) -> List[Dict]:
    """프리셋 전략 실행 (strategy_class가 있는 전략)

    Returns:
        SignalResult dict 리스트
    """
    # 파라미터 변환 (frontend key → backend key)
    converted_params = {}
    for frontend_key, backend_key in param_map.items():
        if frontend_key in params:
            converted_params[backend_key] = params[frontend_key]

    # consecutive 특수 처리
    if strategy_id == 'consecutive' and 'buy_days' in converted_params:
        converted_params['sell_days'] = converted_params['buy_days']

    log("info", f"파라미터: {converted_params}")

    strategy = strategy_class(**converted_params)
    return _run_strategy_on_stocks(strategy, stocks, log, get_stock_name, api_sleep)


def execute_from_builder_state(
    builder_state: Dict[str, Any],
    strategy_name: str,
    stocks: List[str],
    log: Callable,
    get_stock_name: Callable,
    api_sleep: Callable,
) -> List[Dict]:
    """BuilderState에서 전략 실행 (local_ 전략 및 builder-only 전략)

    Returns:
        SignalResult dict 리스트
    """
    log("info", f"빌더 전략: {strategy_name}")
    log("info", f"종목: {', '.join(stocks)}")

    buy_condition, sell_condition = builder_state_to_dsl(builder_state)

    if not buy_condition:
        raise ValueError("매수 조건이 없습니다")

    log("info", f"매수 조건: {buy_condition}")
    if sell_condition:
        log("info", f"매도 조건: {sell_condition}")

    # DSL → AST → 코드 생성 → 동적 로드
    name_snake = sanitize_strategy_name(strategy_name)
    strategy_def = parse_strategy(
        name=name_snake,
        name_ko=strategy_name,
        buy_condition=buy_condition,
        sell_condition=sell_condition or "close < open",
    )

    generator = StrategyCodeGenerator()
    code = generator.generate(strategy_def)

    strategy_instance = _load_strategy_from_code(code, name_snake)
    results = _run_strategy_on_stocks(strategy_instance, stocks, log, get_stock_name, api_sleep)

    log("success", "빌더 전략 실행 완료")
    return results


def execute_custom_file(
    custom_name: str,
    stocks: List[str],
    log: Callable,
    get_stock_name: Callable,
    api_sleep: Callable,
) -> List[Dict]:
    """커스텀 전략 실행 (사용자가 만든 .py 파일)

    Returns:
        SignalResult dict 리스트
    """
    log("info", f"커스텀 전략: {custom_name}")
    log("info", f"종목: {', '.join(stocks)}")

    strategy_file = get_generated_strategy_file(custom_name)

    if not strategy_file.exists():
        raise FileNotFoundError(f"전략 파일을 찾을 수 없습니다: {strategy_file}")
    if not strategy_file.is_file():
        raise ValueError("전략 경로가 일반 파일이 아닙니다")

    spec = importlib.util.spec_from_file_location(f"strategy_{custom_name}", strategy_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    strategy_class = _find_strategy_class(module)
    if not strategy_class:
        raise ValueError("전략 클래스를 찾을 수 없습니다")

    # 사용자 모듈이 정의·import 한 예외 클래스도 경계에서 잡는다
    module_errors = _module_exception_types(module)
    try:
        strategy = strategy_class()
    except module_errors as e:
        raise CustomStrategyError(f"전략 초기화 실패: {type(e).__name__}") from e
    results = _run_strategy_on_stocks(
        strategy, stocks, log, get_stock_name, api_sleep, extra_errors=module_errors,
    )

    log("success", "전략 실행 완료")
    return results


def _load_strategy_from_code(code: str, name_snake: str):
    """생성된 Python 코드를 동적으로 로드하여 전략 인스턴스 반환"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_file = f.name

    try:
        spec = importlib.util.spec_from_file_location(f"temp_strategy_{name_snake}", temp_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        strategy_class = _find_strategy_class(module)
        if not strategy_class:
            raise ValueError("전략 클래스를 생성할 수 없습니다")

        return strategy_class()
    finally:
        os.unlink(temp_file)


class CustomStrategyError(RuntimeError):
    """사용자 전략 코드에서 발생한 예외 (BOUNDARY_ERRORS 로 잡히도록 RuntimeError 상속)"""


def _module_exception_types(module) -> tuple:
    """모듈 네임스페이스에 있는 예외 클래스(사용자 정의·import) 목록"""
    return tuple(
        attr for attr in vars(module).values()
        if isinstance(attr, type) and issubclass(attr, Exception) and attr is not Exception
    )


def _find_strategy_class(module):
    """모듈에서 Strategy 클래스 찾기"""
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and attr_name.endswith('Strategy') and attr_name != 'BaseStrategy':
            return attr
    return None


def _run_strategy_on_stocks(
    strategy,
    stocks: List[str],
    log: Callable,
    get_stock_name: Callable,
    api_sleep: Callable,
    extra_errors: tuple = (),
) -> List[Dict]:
    """전략을 종목 리스트에 대해 실행하고 결과 반환

    extra_errors: 사용자 전략 모듈이 정의한 예외 등 BOUNDARY_ERRORS 밖의 타입
    """
    results = []
    stock_errors = BOUNDARY_ERRORS + extra_errors

    for code in stocks:
        name = get_stock_name(code)
        log("info", f"분석 중: {name} ({code})")

        try:
            signal = strategy.generate_signal(code, name)
            result = {
                'code': code,
                'name': name,
                'action': signal.action.value.upper(),
                'strength': signal.strength,
                'reason': signal.reason,
                'target_price': getattr(signal, 'target_price', None),
            }
            results.append(result)

            action_icon = {"BUY": "▲", "SELL": "▼", "HOLD": "─"}
            action_type = {"BUY": "success", "SELL": "error", "HOLD": "info"}
            log(
                action_type.get(result['action'], "info"),
                f"  {action_icon.get(result['action'], '─')} {result['action']} | 강도: {result['strength']:.2f} | {result['reason']}"
            )
        except stock_errors as e:
            # 종목별 실행 경계: 한 종목 실패가 나머지 종목 실행을 막지 않도록 ERROR 결과로 기록
            log("error", f"  오류: {str(e)}")
            results.append({
                'code': code,
                'name': name,
                'action': 'ERROR',
                'strength': 0,
                'reason': str(e),
                'target_price': None,
            })

        api_sleep()

    return results
