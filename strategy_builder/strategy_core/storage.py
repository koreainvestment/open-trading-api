"""Generated strategy file storage helpers."""

import os
import re
import tempfile
from pathlib import Path


STRATEGY_NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,63}")
STRATEGY_DIR_ENV = "KIS_STRATEGY_DIR"


def validate_strategy_name(name: str) -> str:
    """Validate the opaque identifier used for generated strategy files."""
    if not STRATEGY_NAME_PATTERN.fullmatch(name):
        raise ValueError(f"유효하지 않은 전략 이름: {name!r}")
    return name


def get_generated_strategy_dir() -> Path:
    """Return a private data directory outside the application source tree."""
    configured = os.environ.get(STRATEGY_DIR_ENV)
    root = (
        Path(configured).expanduser()
        if configured
        else Path.home() / ".kis_strategy_builder" / "strategies"
    )

    if root.is_symlink():
        raise ValueError("생성 전략 디렉터리는 symlink일 수 없습니다")

    root = root.resolve(strict=False)
    application_root = Path(__file__).resolve().parents[1]
    if root == application_root or root.is_relative_to(application_root):
        raise ValueError("생성 전략 디렉터리는 애플리케이션 소스 밖에 있어야 합니다")

    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("생성 전략 경로가 디렉터리가 아닙니다")
    return root


def get_generated_strategy_file(name: str) -> Path:
    """Resolve a generated strategy path and enforce root containment."""
    validate_strategy_name(name)
    root = get_generated_strategy_dir()
    path = root / f"strategy_{name}.py"

    if path.parent != root:
        raise ValueError("허용되지 않는 전략 경로")
    if path.is_symlink():
        raise ValueError("생성 전략 파일은 symlink일 수 없습니다")
    return path


def write_generated_strategy(name: str, source: str) -> Path:
    """Atomically create or replace a regular generated strategy file."""
    destination = get_generated_strategy_file(name)
    root = destination.parent

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=root,
            prefix=".strategy-",
            suffix=".tmp",
            delete=False,
        ) as stream:
            # NamedTemporaryFile(mkstemp)은 0o600으로 생성하므로 별도 chmod 불필요
            temporary_path = Path(stream.name)
            stream.write(source)
            stream.flush()
            os.fsync(stream.fileno())

        if destination.is_symlink():
            raise ValueError("생성 전략 파일은 symlink일 수 없습니다")
        os.replace(temporary_path, destination)
        return destination
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
