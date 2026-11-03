"""이슈 #8: stdio JSON-RPC 채널(stdout) 오염 방지 회귀 테스트 (오프라인)."""
import ast
import importlib.util
import logging
import re
import sys
from pathlib import Path
from types import ModuleType

import pytest

MCP_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = MCP_DIR / "tools"
BASE_PATH = TOOLS_DIR / "base.py"

# 자식 프로세스 템플릿 안의 print는 캡처된 파이프로 가므로 검사에서 제외한다.
SERVER_FILES = [
    TOOLS_DIR / "base.py",
    MCP_DIR / "server.py",
    MCP_DIR / "module" / "plugin" / "kis.py",
    MCP_DIR / "module" / "plugin" / "database.py",
    MCP_DIR / "module" / "plugin" / "environment.py",
    MCP_DIR / "module" / "plugin" / "master_file.py",
    MCP_DIR / "module" / "mcp_auth.py",
]


class _AnyInit:
    def __init__(self, *a, **k):
        pass


@pytest.fixture(scope="module")
def base():
    stub_attrs = {
        "fastmcp": ["FastMCP", "Context"],
        "module": [],
        "module.plugin": ["MasterFileManager"],
        "module.plugin.database": ["Database"],
        "module.factory": [],
    }
    for mod_name, attrs in stub_attrs.items():
        mod = ModuleType(mod_name)
        for attr in attrs:
            setattr(mod, attr, type(attr, (_AnyInit,), {}))
        sys.modules[mod_name] = mod
    sys.modules["module.factory"].CONTEXT_REQUEST_ID = "req-id"
    spec = importlib.util.spec_from_file_location("mcp_base_issue08", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcp_base_issue08"] = mod
    spec.loader.exec_module(mod)
    return mod


def _server_side_source(path):
    src = Path(path).read_text(encoding="utf-8")
    if Path(path).name == "base.py":
        src = re.sub(r'API_RUNNER_TEMPLATE = """.*?"""', 'API_RUNNER_TEMPLATE = ""',
                     src, flags=re.DOTALL)
    return src


@pytest.mark.parametrize("path", [str(p) for p in SERVER_FILES],
                         ids=[p.name for p in SERVER_FILES])
def test_no_print_in_server_process(path):
    tree = ast.parse(_server_side_source(path))
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "print"]
    assert calls == []


def test_modify_emits_no_stdout(base, tmp_path, capsys, caplog):
    src = ('def inquire_price(env_dv, pdno):\n'
           '    """docstring"""\n'
           '    pass\n')
    api_file = tmp_path / "api_code.py"
    api_file.write_text(src, encoding="utf-8")
    with caplog.at_level(logging.INFO, logger="mcp_base_issue08"):
        base.ApiExecutor._modify_api_code(
            str(api_file), {"env_dv": "demo", "pdno": "1"},
            "inquire_price", "domestic_stock")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert len(caplog.records) > 0


def test_server_log_level_env_adjustable():
    src = (MCP_DIR / "server.py").read_text(encoding="utf-8")
    assert 'os.getenv("MCP_LOG_LEVEL"' in src
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "basicConfig"):
            assert "_LOG_LEVEL" in ast.dump(n)
            return
    raise AssertionError("logging.basicConfig not found")
