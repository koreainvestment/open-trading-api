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
import re
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List

from strategy_core.dsl.converter import builder_state_to_dsl
from strategy_core.dsl.parser import parse_strategy
from strategy_core.dsl.codegen import StrategyCodeGenerator
from strategy_core.name_utils import sanitize_strategy_name


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
    strategy_dir: str,
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

    # 경로 탐색 방어: 영숫자 + _ 만 허용
    if not re.fullmatch(r'[a-zA-Z0-9_]+', custom_name):
        raise ValueError(f"유효하지 않은 전략 이름: {custom_name!r}")

    strategy_file = Path(strategy_dir) / f"strategy_{custom_name}.py"

    # 부모 디렉터리 이탈 검사
    if not strategy_file.resolve().is_relative_to(Path(strategy_dir).resolve()):
        raise ValueError("허용되지 않는 전략 경로")

    if not strategy_file.exists():
        raise FileNotFoundError(f"전략 파일을 찾을 수 없습니다: {strategy_file}")

    spec = importlib.util.spec_from_file_location(f"strategy_{custom_name}", strategy_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    strategy_class = _find_strategy_class(module)
    if not strategy_class:
        raise ValueError("전략 클래스를 찾을 수 없습니다")

    strategy = strategy_class()
    results = _run_strategy_on_stocks(strategy, stocks, log, get_stock_name, api_sleep)

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
) -> List[Dict]:
    """전략을 종목 리스트에 대해 실행하고 결과 반환"""
    results = []

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
        except Exception as e:
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
