"""경계(boundary) 경로용 예외 튜플

"예외를 절대 전파하지 않아야 하는" 경로(라우트·MCP 툴 진입점, 백그라운드 루프,
배치 per-item 처리, 예제 일괄 실행)에서 `except Exception` 대신 잡는다.
Exception 직계 하위 빌트인 + 이 패키지가 쓰는 라이브러리의 최상위 예외로 구성돼
`except Exception` 과 범위가 같다.

- 새 고유 예외는 RuntimeError 를 상속시키면 별도 추가 없이 포함된다.
- Exception 직계 상속 예외를 가진 서드파티를 새로 도입하면 여기에 추가한다.
- 일반 경로에서는 이 튜플이 아니라 실제 발생 가능한 구체 타입으로 좁혀 잡는다.
"""

import asyncio
import sys
import concurrent.futures
import csv
import http.client
import pickle
import queue
import struct
import re
import subprocess
import zipfile
import zlib

import httpx
import urllib3.exceptions
import jinja2
import pandas as pd
import yaml
from websockets.exceptions import WebSocketException

from .exceptions import LeanError

_BUILTIN_ERRORS = (
    ArithmeticError,
    AssertionError,
    AttributeError,
    BufferError,
    EOFError,
    ImportError,
    LookupError,
    MemoryError,
    NameError,
    OSError,
    ReferenceError,
    RuntimeError,
    StopAsyncIteration,
    StopIteration,
    SyntaxError,
    SystemError,
    TypeError,
    ValueError,
    Warning,
    ExceptionGroup,
)

_STDLIB_ERRORS = (
    csv.Error,
    http.client.HTTPException,
    pickle.PickleError,
    queue.Empty,
    queue.Full,
    struct.error,
    zlib.error,
    re.error,
    subprocess.SubprocessError,
    concurrent.futures.CancelledError,
    concurrent.futures.InvalidStateError,
    zipfile.BadZipFile,
    asyncio.InvalidStateError,
    asyncio.LimitOverrunError,
    asyncio.QueueEmpty,
    asyncio.QueueFull,
)

# pandas.errors 중 Exception 직계 상속 예외 (InvalidIndexError 등은 인덱싱/재색인에서 발생)
_PANDAS_ERRORS = (
    pd.errors.InvalidIndexError,
    pd.errors.DataError,
    pd.errors.SpecificationError,
    pd.errors.IndexingError,
    pd.errors.PossibleDataLossError,
    pd.errors.ClosedFileError,
    pd.errors.NumbaUtilError,
)

# plotly 는 report 에서 지연 import(ImportError 시 안내 문구) 하는 선택 의존성
try:
    from plotly.exceptions import PlotlyError
    _OPTIONAL_ERRORS = (PlotlyError,)
except ImportError:
    _OPTIONAL_ERRORS = ()

_LIBRARY_ERRORS = (
    httpx.HTTPError,
    urllib3.exceptions.HTTPError,
    httpx.InvalidURL,
    httpx.CookieConflict,
    jinja2.TemplateError,
    WebSocketException,
    yaml.YAMLError,
    LeanError,
)

# Python 3.13+ 에만 있는 Exception 직계 예외
_VERSION_ERRORS = tuple(
    t for t in (getattr(asyncio, "QueueShutDown", None),) if t is not None
)

BOUNDARY_ERRORS = (
    _BUILTIN_ERRORS + _STDLIB_ERRORS + _PANDAS_ERRORS + _LIBRARY_ERRORS + _OPTIONAL_ERRORS + _VERSION_ERRORS
)

# 취소·종료 신호까지 잡아 "기록 후 다시 raise" 하는 자리 전용
ABORT_ERRORS = BOUNDARY_ERRORS + (
    BaseExceptionGroup,
    KeyboardInterrupt,
    SystemExit,
    GeneratorExit,
    asyncio.CancelledError,
)


def _exception_types_in(values) -> list:
    return [
        v for v in values
        if isinstance(v, type) and issubclass(v, Exception) and v is not Exception
    ]


def _user_namespaces(obj):
    """콜백·컴포넌트가 참조할 수 있는 이름공간: 함수의 전역·클로저, 그 외엔 정의 모듈"""
    func = getattr(obj, "__func__", obj)                 # bound method → 함수
    if hasattr(func, "__globals__"):
        yield func.__globals__.values()
        for cell in getattr(func, "__closure__", None) or ():
            try:
                yield (cell.cell_contents,)
            except ValueError:                           # 비어 있는 셀
                continue
        return
    module = sys.modules.get(getattr(obj, "__module__", None) or "")
    if module is not None:
        yield vars(module).values()


def user_code_errors(*user_objects) -> tuple:
    """사용자 코드(콜백·컴포넌트) 경계용 예외 튜플.

    BOUNDARY_ERRORS 에 더해, 사용자 객체가 참조하는 이름공간(함수 전역·클로저, 정의 모듈)의
    예외 클래스(사용자 정의 `class MyErr(Exception)` 포함)를 더한다.
    except 절의 타입 식은 예외 발생 시점에 평가되므로 비용은 실패 경로에서만 든다.
    """
    extra = []
    for obj in user_objects:
        for values in _user_namespaces(obj):
            for t in _exception_types_in(values):
                if t not in extra:
                    extra.append(t)
    return BOUNDARY_ERRORS + tuple(extra)
