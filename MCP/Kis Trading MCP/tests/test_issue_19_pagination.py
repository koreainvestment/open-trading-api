"""이슈 #19: tr_cont 판정 통일·잘림 명시 스윕 테스트 (오프라인)."""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCOPE_DIRS = [REPO_ROOT / "examples_llm", REPO_ROOT / "examples_user"]
EXCLUDE_NAMES = {"kis_auth.py"}
BANNED = [
    'tr_cont == "M"',
    'tr_cont in ["M", "F"]',
    '"Max recursive depth reached."',
]


def _scope_files():
    for d in SCOPE_DIRS:
        for p in sorted(d.rglob("*.py")):
            if p.name in EXCLUDE_NAMES:
                continue
            yield p


def test_no_legacy_pagination_checks():
    offenders = []
    for p in _scope_files():
        try:
            src = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pat in BANNED:
            if pat in src:
                offenders.append(f"{p.relative_to(REPO_ROOT)}: {pat}")
    assert offenders == []


def test_helper_defined_where_used():
    missing, dupes, used = [], [], 0
    for p in _scope_files():
        try:
            src = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "_has_next_page(tr_cont)" not in src:
            continue
        used += 1
        n = src.count("def _has_next_page")
        if n == 0:
            missing.append(str(p.relative_to(REPO_ROOT)))
        elif n > 1:
            dupes.append(str(p.relative_to(REPO_ROOT)))
    assert used > 0
    assert missing == []
    assert dupes == []
