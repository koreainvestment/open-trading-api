"""
경계(boundary) 경로용 예외 튜플

"예외를 절대 전파하지 않아야 하는" 경로(라우트 진입점, 웹소켓/폴링 루프,
배치 per-item 처리, 전략 실행 루프, 예제 일괄 실행)에서 `except Exception` 대신 잡는다.
Exception 직계 하위 빌트인 + 이 패키지가 쓰는 라이브러리의 최상위 예외로 구성돼
`except Exception` 과 범위가 같다.

- 새 고유 예외는 RuntimeError 를 상속시키면 별도 추가 없이 포함된다.
- Exception 직계 상속 예외를 가진 서드파티를 새로 도입하면 여기에 추가한다.
- 일반 경로(파일 읽기, 파싱 등)에서는 이 튜플이 아니라 실제 발생 가능한 구체 타입으로 좁혀 잡는다.
- requests.RequestException 은 OSError 하위, pydantic.ValidationError 는 ValueError 하위라 별도 추가 불필요.
"""

import asyncio
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
import pandas as pd
import yaml
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.exceptions import WebSocketException as StarletteWebSocketException
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import WebSocketException

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
    re.error,
    subprocess.SubprocessError,
    concurrent.futures.CancelledError,
    concurrent.futures.InvalidStateError,
    zipfile.BadZipFile,
    zipfile.LargeZipFile,
    zlib.error,
    asyncio.InvalidStateError,
    asyncio.LimitOverrunError,
    asyncio.QueueEmpty,
    asyncio.QueueFull,
)

# pandas.errors 중 Exception 직계 상속 예외
_PANDAS_ERRORS = (
    pd.errors.InvalidIndexError,
    pd.errors.DataError,
    pd.errors.SpecificationError,
    pd.errors.IndexingError,
    pd.errors.PossibleDataLossError,
    pd.errors.ClosedFileError,
    pd.errors.NumbaUtilError,
)

_LIBRARY_ERRORS = (
    httpx.HTTPError,
    urllib3.exceptions.HTTPError,
    httpx.InvalidURL,
    httpx.CookieConflict,
    yaml.YAMLError,
    WebSocketException,
    StarletteHTTPException,
    StarletteWebSocketException,
    WebSocketDisconnect,
)

# Python 3.13+ 에만 있는 Exception 직계 예외
_VERSION_ERRORS = tuple(
    t for t in (getattr(asyncio, "QueueShutDown", None),) if t is not None
)

BOUNDARY_ERRORS = (
    _BUILTIN_ERRORS + _STDLIB_ERRORS + _PANDAS_ERRORS + _LIBRARY_ERRORS + _VERSION_ERRORS
)

# 취소·종료 신호까지 잡아 "기록 후 다시 raise" 하는 자리 전용
ABORT_ERRORS = BOUNDARY_ERRORS + (
    BaseExceptionGroup,
    KeyboardInterrupt,
    SystemExit,
    GeneratorExit,
    asyncio.CancelledError,
)
