"""kis_auth.py 6종 복제본 회귀 테스트 (이슈 #11~#18).

KIS API를 호출하지 않는다. 각 복제본을 격리된 HOME(임시 디렉터리)에서
import하고 requests.post/get를 가짜 응답으로 대체한다.
"""

import importlib.util
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

COPIES = {
    "examples_user": "examples_user/kis_auth.py",
    "examples_llm": "examples_llm/kis_auth.py",
    "backtester": "backtester/kis_auth.py",
    "strategy_builder": "strategy_builder/kis_auth.py",
    "legacy_sample01": "legacy/Sample01/kis_auth.py",
    "legacy_rest": "legacy/rest/kis_auth.py",
}

MODERN = ["examples_user", "examples_llm", "backtester", "strategy_builder"]
WITH_URL_FETCH = MODERN + ["legacy_sample01"]

FIXTURE_CFG = {
    "my_app": "DUMMY_APP",
    "my_sec": "DUMMY_SEC",
    "paper_app": "DUMMY_PAPER_APP",
    "paper_sec": "DUMMY_PAPER_SEC",
    "my_htsid": "DUMMY_HTS",
    "my_acct_stock": "12345678",
    "my_acct_future": "12345678",
    "my_paper_stock": "12345678",
    "my_paper_future": "12345678",
    "my_prod": "01",
    "prod": "https://openapi.koreainvestment.com:9443",
    "ops": "ws://ops.koreainvestment.com:21000",
    "vps": "https://openapivts.koreainvestment.com:29443",
    "vops": "ws://ops.koreainvestment.com:31000",
    "my_token": "",
    "my_agent": "test-agent",
}


_counter = 0


class FakeResp:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {"rt_cd": "0", "msg_cd": "00000000", "msg1": "OK"}
        self.headers = {}
        self.text = str(self._payload)

    def json(self):
        return self._payload


LOAD_BLOCKED = FakeResp(500, {"rt_cd": "1", "msg_cd": "EGW00123", "msg1": "blocked"})


def load_copy(name, tmp_path, monkeypatch):
    """복제본 하나를 격리 HOME에서 import한다. 매번 새 모듈 객체."""
    global _counter
    _counter += 1
    home = tmp_path / f"home_{name}_{_counter}"
    cfg_dir = home / "KIS" / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "kis_devlp.yaml").write_text(
        yaml.safe_dump(FIXTURE_CFG), encoding="utf-8"
    )
    monkeypatch.setenv("HOME", str(home))
    # legacy 복제본은 KIS_CONFIG_DIR 환경변수로 설정 경로를 지정한다
    monkeypatch.setenv("KIS_CONFIG_DIR", str(cfg_dir))
    # expanduser 캐시 무효화 (3.8+는 캐시 없음, 안전장치)
    if hasattr(os, "environ"):
        pass
    mod_name = f"kis_auth_{name}_{_counter}"
    spec = importlib.util.spec_from_file_location(
        mod_name, REPO_ROOT / COPIES[name]
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    # import 시점의 네트워크 호출(legacy/rest의 auth() 등)을 원천 차단한다
    monkeypatch.setattr("requests.post", lambda *a, **k: LOAD_BLOCKED)
    monkeypatch.setattr("requests.get", lambda *a, **k: LOAD_BLOCKED)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(params=list(COPIES))
def any_copy(request, tmp_path, monkeypatch):
    return request.param, load_copy(request.param, tmp_path, monkeypatch)


@pytest.fixture(params=MODERN)
def modern_copy(request, tmp_path, monkeypatch):
    return request.param, load_copy(request.param, tmp_path, monkeypatch)


@pytest.fixture(params=WITH_URL_FETCH)
def fetch_copy(request, tmp_path, monkeypatch):
    return request.param, load_copy(request.param, tmp_path, monkeypatch)


# ---- 이슈 #11: reAuth가 24시간 뒤 실제로 동작한다 ----

def test_reauth_fires_after_24h(any_copy, monkeypatch):
    _, mod = any_copy
    calls = []
    monkeypatch.setattr(mod, "auth", lambda svr, product: calls.append((svr, product)))
    mod._last_svr = "vps"
    mod._last_product = "01"
    mod._last_auth_time = datetime.now() - timedelta(hours=25)
    mod.reAuth()
    assert calls == [("vps", "01")]


def test_reauth_sleeps_before_24h(any_copy, monkeypatch):
    _, mod = any_copy
    calls = []
    monkeypatch.setattr(mod, "auth", lambda svr, product: calls.append((svr, product)))
    mod._last_auth_time = datetime.now() - timedelta(hours=23)
    mod.reAuth()
    assert calls == []


def test_reauth_never_flips_to_prod(any_copy, monkeypatch):
    """인자 없이 호출해도 기억한 모의 서버를 실전으로 바꾸지 않는다."""
    _, mod = any_copy
    calls = []
    monkeypatch.setattr(mod, "auth", lambda svr, product: calls.append((svr, product)))
    mod._last_svr = "vps"
    mod._last_product = "01"
    mod._last_auth_time = datetime.now() - timedelta(hours=30)
    mod.reAuth()
    assert calls and calls[0][0] == "vps"


def test_reauth_guard_blocks_reentry(any_copy, monkeypatch):
    _, mod = any_copy
    calls = []
    monkeypatch.setattr(mod, "auth", lambda svr, product: calls.append((svr, product)))
    mod._last_auth_time = datetime.now() - timedelta(hours=30)
    mod._reauth_running = True
    try:
        mod.reAuth()
    finally:
        mod._reauth_running = False
    assert calls == []


def test_expiry_response_retries_once(fetch_copy, monkeypatch):
    """EGW00123이면 1회 재인증 후 재시도하고, 두 번째는 그대로 반환한다."""
    _, mod = fetch_copy
    expired = FakeResp(200, {"rt_cd": "1", "msg_cd": "EGW00123", "msg1": "만료"})
    ok = FakeResp(200, {"rt_cd": "0", "msg_cd": "00000000", "msg1": "OK"})
    calls = {"n": 0}

    def fake_post(*a, **k):
        calls["n"] += 1
        return expired if calls["n"] == 1 else ok

    monkeypatch.setattr(mod.requests, "post", fake_post)
    monkeypatch.setattr(mod.requests, "get", fake_post)
    reauths = []
    monkeypatch.setattr(mod, "reAuth", lambda *a, **k: reauths.append(1))
    monkeypatch.setattr(mod, "getTREnv", lambda: SimpleNamespace(my_url="https://x"))
    monkeypatch.setattr(mod, "_getBaseHeader", lambda: {})
    res = mod._url_fetch("/uapi/test", "TTTC0012U", "", {}, None, True, False)
    assert res.isOK()
    assert len(reauths) == 1


# ---- 이슈 #12: changeTREnv가 모드별 호출 간격을 실제로 바꾼다 ----

def test_change_trenv_updates_smart_sleep(any_copy):
    """모의(vps) 0.5초·실전(prod) 0.05초가 모듈 전역에 반영된다."""
    _, mod = any_copy
    if not hasattr(mod, "_smartSleep"):
        pytest.skip("이 복제본에는 _smartSleep이 없다(legacy)")
    mod.changeTREnv("DUMMYTOKEN", "vps", "01")
    assert mod._isPaper is True
    assert mod._smartSleep == 0.5
    mod.changeTREnv("DUMMYTOKEN", "prod", "01")
    assert mod._isPaper is False
    assert mod._smartSleep == 0.05


# ---- 이슈 #13: 방금 발급된 토큰이 _TRENV.my_token에 저장된다 ----

def test_change_trenv_stores_new_token(any_copy):
    name, mod = any_copy
    if name.startswith("legacy_"):
        pytest.skip("legacy 복제본은 토큰 저장 규약이 달라 제외")
    mod.changeTREnv("NEWTOKEN123", "vps", "01")
    assert mod.getTREnv().my_token == "NEWTOKEN123"
    # falsy 토큰이면 기존 값을 유지한다(auth_ws의 changeTREnv(None, ...) 경로)
    mod.changeTREnv(None, "vps", "01")
    assert mod.getTREnv().my_token == "NEWTOKEN123"


# ---- 이슈 #14: 토큰 발급 실패는 조용히 넘기지 않고 예외를 던진다 ----

def test_auth_failure_raises(any_copy, monkeypatch):
    _, mod = any_copy
    monkeypatch.setattr(mod.requests, "post", lambda *a, **k: FakeResp(500, {"rt_cd": "1", "msg_cd": "EGW00123", "msg1": "fail"}))
    with pytest.raises(RuntimeError):
        mod.auth(svr="vps", product="01")


@pytest.mark.parametrize("name", ["backtester", "strategy_builder"])
def test_auth_ws_failure_raises(name, tmp_path, monkeypatch):
    mod = load_copy(name, tmp_path, monkeypatch)
    monkeypatch.setattr(mod.requests, "post", lambda *a, **k: FakeResp(500, {"rt_cd": "1", "msg_cd": "EGW00123", "msg1": "fail"}))
    with pytest.raises(RuntimeError):
        mod.auth_ws(svr="vps", product="01")


# ---- 이슈 #15: 실전/모의 토큰 파일을 분리하고 앱키로 귀속한다 ----

def _seed_token(mod, token, svr):
    mod.save_token(token, "2099-01-01 00:00:00", svr)


def test_token_files_are_per_server(any_copy):
    _, mod = any_copy
    _seed_token(mod, "PRODTOK", "prod")
    assert mod.read_token("vps") is None
    assert mod.read_token("prod") == "PRODTOK"
    _seed_token(mod, "VPSTOK", "vps")
    assert mod.read_token("prod") == "PRODTOK"
    assert mod.read_token("vps") == "VPSTOK"


def test_appkey_change_discards_token(any_copy):
    _, mod = any_copy
    _seed_token(mod, "PRODTOK", "prod")
    assert mod.read_token("prod") == "PRODTOK"
    mod._cfg["my_app"] = "ROTATED_APP"
    try:
        assert mod.read_token("prod") is None
    finally:
        mod._cfg["my_app"] = "DUMMY_APP"


def _load_provider(tmp_path, monkeypatch):
    import base64
    import importlib.util
    home = tmp_path / "prov_home"
    cfg_dir = home / "KIS" / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "kis_devlp.yaml").write_text(yaml.safe_dump(FIXTURE_CFG), encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("KIS_CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr("requests.post", lambda *a, **k: LOAD_BLOCKED)
    monkeypatch.setattr("requests.get", lambda *a, **k: LOAD_BLOCKED)
    spec = importlib.util.spec_from_file_location(
        "kis_provider_auth",
        REPO_ROOT / "backtester" / "kis_backtest" / "providers" / "kis" / "auth.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kis_provider_auth"] = mod
    spec.loader.exec_module(mod)
    return mod, cfg_dir


def _live_jwt(appkey):
    import base64
    import json
    b = lambda o: base64.urlsafe_b64encode(json.dumps(o).encode()).decode()
    return f"{b({'alg': 'none'})}.{b({'jti': appkey})}.sig"


def test_from_env_requires_explicit_live(tmp_path, monkeypatch):
    import hashlib
    from datetime import datetime
    pa, cfg_dir = _load_provider(tmp_path, monkeypatch)
    fp = hashlib.sha256(b"DUMMY_APP").hexdigest()[:16]
    (cfg_dir / f"KIS{datetime.today().strftime('%Y%m%d')}_prod").write_text(
        yaml.safe_dump({"token": _live_jwt("DUMMY_APP"),
                        "valid-date": datetime(2099, 1, 1),
                        "appkey-sha": fp}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        pa.KISAuth.from_env()
    # 이후는 모드 결정만 본다. 실제 발급은 가짜 처리한다.
    authed = []
    monkeypatch.setattr(pa.ka, "auth", lambda svr, product: authed.append(svr))
    monkeypatch.setattr(pa.ka, "getTREnv",
                        lambda: SimpleNamespace(my_url="https://x"))
    assert pa.KISAuth.from_env(mode="live").is_paper is False
    assert authed == ["prod"]
    assert pa.KISAuth.from_env(mode="paper").is_paper is True
    assert authed == ["prod", "vps"]


# ---- 이슈 #17: 웹소켓 구독 상한·해제·배치 파싱 ----

def _fake_request(tr_type, data):
    return ({"header": {"tr_type": tr_type},
             "body": {"input": {"tr_id": "H0STCNT0"}}}, ["c1", "c2"])


def test_cap_counts_items_not_trs(modern_copy, monkeypatch):
    _, mod = modern_copy
    monkeypatch.setattr(mod, "smart_sleep", lambda: None)
    for i in range(21):
        mod.add_open_map(f"f{i}", _fake_request, ["a", "b"])
    assert mod.open_subscription_count() == 42


def test_runner_rejects_over_cap(modern_copy):
    import asyncio
    _, mod = modern_copy
    for i in range(41):
        mod.add_open_map(f"f{i}", _fake_request, ["x"])
    with pytest.raises(ValueError):
        asyncio.run(mod.KISWebSocket("")._KISWebSocket__runner())


def test_unsubscribe_sends_unsub(modern_copy, monkeypatch):
    import asyncio
    import json
    _, mod = modern_copy
    monkeypatch.setattr(mod, "smart_sleep", lambda: None)
    sent = []

    class FakeWS:
        async def send(self, msg):
            sent.append(json.loads(msg))

    asyncio.run(mod.KISWebSocket("").unsubscribe(FakeWS(), _fake_request, "005930"))
    assert sent and sent[0]["header"]["tr_type"] == "2"


def _run_subscriber(mod, raw):
    import asyncio
    seen = {}

    class FakeWS:
        def __aiter__(self):
            async def gen():
                yield raw
            return gen()

    ksw = mod.KISWebSocket("")
    ksw.on_result = lambda ws, tr_id, df, dm: seen.update(df=df)
    mod.add_data_map(tr_id="H0STCNT0", columns=["c1", "c2"])
    asyncio.run(ksw._KISWebSocket__subscriber(FakeWS()))
    return seen["df"]


def test_batch_records_reshape(modern_copy):
    _, mod = modern_copy
    df = _run_subscriber(mod, "0|H0STCNT0|2|a^b^c^d")
    assert df.shape == (2, 2)
    assert df.iloc[1].tolist() == ["c", "d"]


def test_single_record_unchanged(modern_copy):
    _, mod = modern_copy
    df = _run_subscriber(mod, "0|H0STCNT0|1|a^b")
    assert df.shape == (1, 2)


LEGACY_WS_FIXES = [
    "legacy/websocket/python/ws_domestic_stock.py",
    "legacy/websocket/python/multi_processing_sample_ws.py",
]


@pytest.mark.parametrize("rel", LEGACY_WS_FIXES)
def test_legacy_signing_notice_defined(rel):
    import ast
    src = (REPO_ROOT / rel).read_text(encoding="utf-8")
    tree = ast.parse(src)
    called = {n.func.id for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    defined = {n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "stocksigningnotice" not in called - defined
    assert "stocksigningnotice_domestic" in called


# ---- 이슈 #18: 시크릿 마스킹·원자적 저장 ----

def test_save_token_mode_0600(any_copy):
    import os
    import stat
    from datetime import datetime, timedelta
    _, mod = any_copy
    future = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    mod.save_token('TOK123SECRET', future, 'prod')
    path = mod._token_path('prod')
    assert os.path.isfile(path)
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    content = open(path, encoding='utf-8').read()
    assert 'TOK123SECRET' in content
    assert mod.read_token('prod') == 'TOK123SECRET'
    leftovers = [f for f in os.listdir(os.path.dirname(path) or '.')
                 if f.startswith('.kis_token_')]
    assert leftovers == []


def test_no_full_loader():
    rels = list(COPIES.values()) + ['legacy/rest/kis_api.py']
    for rel in rels:
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        assert 'FullLoader' not in src, rel
        assert 'safe_load' in src, rel


def test_token_placeholder_uses_with_block():
    for name, rel in COPIES.items():
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        assert 'open(token_tmp, "w+")' not in src, name


def test_ws_log_masks_secrets(modern_copy):
    import json
    _, mod = modern_copy
    for helper in ('_mask_ws_raw', '_masked_json', '_redacted_headers'):
        assert callable(getattr(mod, helper, None)), helper
    raw = json.dumps({
        'header': {'tr_id': 'H0STCNT0'},
        'body': {'input': {
            'approval_key': 'SENTINEL_APPROVAL_123',
            'key': 'SENTINEL_KEY_456',
            'iv': 'SENTINEL_IV_789',
        }},
    })
    masked_raw = mod._mask_ws_raw(raw)
    assert 'SENTINEL_APPROVAL_123' not in masked_raw
    assert 'SENTINEL_KEY_456' not in masked_raw
    assert 'SENTINEL_IV_789' not in masked_raw
    assert '***' in masked_raw
    masked_json = mod._masked_json(raw)
    assert 'SENTINEL_APPROVAL_123' not in masked_json
    assert 'SENTINEL_KEY_456' not in masked_json
    assert 'SENTINEL_IV_789' not in masked_json
    assert '***' in masked_json
    masked_headers = mod._redacted_headers({
        'authorization': 'SENTINEL_AUTH_000',
        'appsecret': 'SENTINEL_APPSECRET_111',
        'tr_id': 'H0STCNT0',
    })
    assert 'SENTINEL_AUTH_000' not in str(masked_headers)
    assert 'SENTINEL_APPSECRET_111' not in str(masked_headers)
    assert '***' in str(masked_headers)


def test_legacy_rest_no_token_print():
    src = (REPO_ROOT / 'legacy/rest/kis_auth.py').read_text(encoding='utf-8')
    assert 'print("saved_token' not in src
    assert 'print(gettoken)' not in src


def test_legacy_ws_masks_approval_key():
    ws_dir = REPO_ROOT / 'legacy/websocket/python'
    rels = sorted(p for p in ws_dir.glob('*.py'))
    assert len(rels) == 9
    for p in rels:
        src = p.read_text(encoding='utf-8')
        assert 'print("approval_key [%s]" % (g_approval_key))' not in src, p.name
