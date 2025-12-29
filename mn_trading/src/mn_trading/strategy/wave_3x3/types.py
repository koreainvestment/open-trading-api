# This module exists to define the typed adapter request/response contracts.

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Wave3x3RunRequest:
    codes: list[str]
    zones_csv: str
    engine_out_dir: str
    data_dir: str | None = None
    asof: str | None = None
    extra_args: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Wave3x3RunResult:
    returncode: int
    stdout: str
    stderr: str
    outputs: dict[str, str]
    asof: str | None
    codes: list[str]
