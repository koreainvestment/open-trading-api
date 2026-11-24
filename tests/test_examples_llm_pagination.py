"""examples_llm 전수 점검 회귀 테스트 (이슈 #28).

KIS API를 호출하지 않는다. 가짜 kis_auth 스텁으로 페이지 시나리오를
재생한다:
- 순위 8종 무한 재귀 가드 (depth/max_depth + CTX 전달)
- pension_inquire_present_balance 연속조회 누락 복구
"""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
LLM = REPO_ROOT / "examples_llm"

RANK_FILES = [
    "domestic_stock/finance_ratio/finance_ratio.py",
    "domestic_stock/fluctuation/fluctuation.py",
    "domestic_stock/market_cap/market_cap.py",
    "domestic_stock/market_value/market_value.py",
    "domestic_stock/near_new_highlow/near_new_highlow.py",
    "domestic_stock/profit_asset_index/profit_asset_index.py",
    "domestic_stock/quote_balance/quote_balance.py",
    "domestic_stock/volume_rank/volume_rank.py",
]


class FakeResp:
    def __init__(self, body, header):
        self._body = SimpleNamespace(**body)
        self._header = SimpleNamespace(**header)

    def isOK(self):
        return True

    def getBody(self):
        return self._body

    def getHeader(self):
        return self._header

    def printError(self, url=""):
        raise AssertionError(f"unexpected error path for {url}")


class FakeKa:
    """페이지 스크립트를 순서대로 반환하는 kis_auth 스텁."""

    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []

    def _url_fetch(self, api_url, tr_id, tr_cont, params):
        self.calls.append(SimpleNamespace(api_url=api_url, tr_id=tr_id, tr_cont=tr_cont, params=dict(params)))
        if len(self.pages) > 1:
            page = self.pages.pop(0)
        else:
            page = self.pages[0]  # 마지막 페이지 반복 (무한 M 시나리오용)
        return FakeResp(page["body"], page["header"])

    def smart_sleep(self):
        pass


def load_sample(relpath, stub):
    sys.modules["kis_auth"] = stub
    try:
        spec = importlib.util.spec_from_file_location("sample_under_test", LLM / relpath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.modules.pop("kis_auth", None)


VOLUME_RANK_KWARGS = dict(
    fid_cond_mrkt_div_code="J",
    fid_cond_scr_div_code="20171",
    fid_input_iscd="0002",
    fid_div_cls_code="0",
    fid_blng_cls_code="0",
    fid_trgt_cls_code="111111111",
    fid_trgt_exls_cls_code="0000000000",
    fid_input_price_1="0",
    fid_input_price_2="1000000",
    fid_vol_cnt="100000",
    fid_input_date_1="",
)


def rank_pages(*tr_conts):
    return [
        {
            "body": {"output": [{"row": i}]},
            "header": {"tr_cont": tc, "ctx_area_fk": f"FK{i}", "ctx_area_nk": f"NK{i}"},
        }
        for i, tc in enumerate(tr_conts)
    ]


def test_volume_rank_accumulates_pages_and_forwards_ctx():
    stub = FakeKa(rank_pages("M", "M", ""))
    mod = load_sample("domestic_stock/volume_rank/volume_rank.py", stub)
    df = mod.volume_rank(**VOLUME_RANK_KWARGS)
    assert len(df) == 3
    assert [c.tr_cont for c in stub.calls] == ["", "N", "N"]
    # 1페이지 응답 ctx가 2페이지 요청에 그대로 전달된다
    assert stub.calls[1].params["CTX_AREA_FK"] == "FK0"
    assert stub.calls[1].params["CTX_AREA_NK"] == "NK0"
    assert stub.calls[2].params["CTX_AREA_FK"] == "FK1"
    assert stub.calls[2].params["CTX_AREA_NK"] == "NK1"


def test_volume_rank_endless_next_terminates_at_max_depth(caplog):
    stub = FakeKa(rank_pages("M"))
    mod = load_sample("domestic_stock/volume_rank/volume_rank.py", stub)
    with caplog.at_level("WARNING"):
        df = mod.volume_rank(**VOLUME_RANK_KWARGS, max_depth=3)
    assert len(stub.calls) == 4  # 초기 1회 + 재귀 3회
    assert len(df) == 4
    assert any("truncated" in r.message for r in caplog.records)


def test_pension_present_balance_paginates():
    pages = [
        {
            "body": {
                "output1": [{"stk": "A"}],
                "output2": [{"tot": 1}],
                "ctx_area_fk100": "PFK1",
                "ctx_area_nk100": "PNK1",
            },
            "header": {"tr_cont": "M"},
        },
        {
            "body": {"output1": [{"stk": "B"}], "output2": [{"tot": 2}]},
            "header": {"tr_cont": ""},
        },
    ]
    stub = FakeKa(pages)
    mod = load_sample("domestic_stock/pension_inquire_present_balance/pension_inquire_present_balance.py", stub)
    df1, df2 = mod.pension_inquire_present_balance(cano="12345678", acnt_prdt_cd="29", user_dvsn_cd="00")
    assert len(df1) == 2 and len(df2) == 2
    assert [c.tr_cont for c in stub.calls] == ["", "N"]
    assert stub.calls[1].params["CTX_AREA_FK100"] == "PFK1"
    assert stub.calls[1].params["CTX_AREA_NK100"] == "PNK1"


def test_all_self_recursive_samples_are_guarded():
    """스스로를 호출하는 모든 샘플 함수는 depth/max_depth를 가져야 한다."""
    import ast

    offenders = []
    for path in sorted(LLM.rglob("*.py")):
        if path.name.startswith("chk_") or path.name == "kis_auth.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            calls_self = any(
                isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == node.name
                for n in ast.walk(node)
            )
            if not calls_self:
                continue
            args = [a.arg for a in node.args.args]
            if "depth" not in args or "max_depth" not in args:
                offenders.append(f"{path.relative_to(LLM)}::{node.name}")
    assert offenders == []


def test_no_legacy_pagination_markers():
    for path in sorted(LLM.rglob("*.py")):
        if path.name == "kis_auth.py":
            continue
        src = path.read_text(encoding="utf-8")
        assert 'tr_cont == "M"' not in src, path
        assert 'print("Call Next")' not in src, path
        assert 'print("The End")' not in src, path
