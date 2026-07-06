import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

MCP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MCP_ROOT))

from tools.base import ApiExecutor, ALLOWED_ENV_DV  # noqa: E402

MALICIOUS_ENV_DV = (
    "real)\n"
    "__import__('pathlib').Path('/tmp/kis_mcp_env_dv_rce_proof.txt').write_text('owned')\n"
    "raise SystemExit(0)\n"
    " #"
)


class ApiExecutorSecurityTest(unittest.TestCase):
    def setUp(self):
        self.executor = ApiExecutor("domestic_stock")

    def test_validate_env_dv_rejects_injection_payload(self):
        with self.assertRaises(ValueError):
            ApiExecutor._validate_env_dv(MALICIOUS_ENV_DV)

    def test_validate_env_dv_accepts_allowed_values(self):
        for value in ALLOWED_ENV_DV:
            self.assertEqual(ApiExecutor._validate_env_dv(value), value)

    def test_modify_api_code_passes_validated_env_dv_to_function(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            api_code_path = os.path.join(temp_dir, "api_code.py")
            with open(api_code_path, "w", encoding="utf-8") as f:
                f.write(
                    "def inquire_price(env_dv, fid_cond_mrkt_div_code, fid_input_iscd):\n"
                    "    return {'env_dv': env_dv}\n"
                )

            ApiExecutor._modify_api_code(
                api_code_path,
                {
                    "env_dv": "real",
                    "fid_cond_mrkt_div_code": "J",
                    "fid_input_iscd": "005930",
                },
                "inquire_price",
            )

            params_path = os.path.join(temp_dir, "params.json")
            with open(params_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            self.assertEqual(payload["env_dv"], "real")
            self.assertEqual(payload["params"]["env_dv"], "real")

    def test_modify_api_code_blocks_malicious_env_dv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            api_code_path = os.path.join(temp_dir, "api_code.py")
            with open(api_code_path, "w", encoding="utf-8") as f:
                f.write("def inquire_price(fid_cond_mrkt_div_code, fid_input_iscd, env_dv='demo'):\n"
                        "    return {'ok': True}\n")

            with self.assertRaises(ValueError):
                ApiExecutor._modify_api_code(
                    api_code_path,
                    {
                        "env_dv": MALICIOUS_ENV_DV,
                        "fid_cond_mrkt_div_code": "J",
                        "fid_input_iscd": "005930",
                    },
                    "inquire_price",
                )

    def test_modify_api_code_uses_params_json_without_user_input_in_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            api_code_path = os.path.join(temp_dir, "api_code.py")
            with open(api_code_path, "w", encoding="utf-8") as f:
                f.write("def inquire_price(fid_cond_mrkt_div_code, fid_input_iscd):\n"
                        "    return {'price': 1}\n")

            ApiExecutor._modify_api_code(
                api_code_path,
                {
                    "env_dv": "demo",
                    "fid_cond_mrkt_div_code": "J",
                    "fid_input_iscd": "005930",
                },
                "inquire_price",
            )

            with open(api_code_path, "r", encoding="utf-8") as f:
                generated = f.read()

            self.assertNotIn("env_dv=", generated)
            self.assertIn("params.json", generated)

            params_path = os.path.join(temp_dir, "params.json")
            self.assertTrue(os.path.exists(params_path))
            with open(params_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            self.assertEqual(payload["env_dv"], "demo")
            self.assertEqual(payload["params"]["fid_input_iscd"], "005930")

    def test_generated_runner_does_not_execute_injected_code(self):
        proof_path = "/tmp/kis_mcp_env_dv_rce_proof.txt"
        if os.path.exists(proof_path):
            os.remove(proof_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            api_code_path = os.path.join(temp_dir, "api_code.py")
            with open(api_code_path, "w", encoding="utf-8") as f:
                f.write("def inquire_price(fid_cond_mrkt_div_code, fid_input_iscd):\n"
                        "    return {'price': 1}\n")

            with self.assertRaises(ValueError):
                ApiExecutor._modify_api_code(
                    api_code_path,
                    {"env_dv": MALICIOUS_ENV_DV, "fid_cond_mrkt_div_code": "J", "fid_input_iscd": "005930"},
                    "inquire_price",
                )

        self.assertFalse(os.path.exists(proof_path))


class McpAuthMiddlewareTest(unittest.TestCase):
    def test_http_mode_requires_access_token(self):
        from module.mcp_auth import ensure_http_access_token

        with self.assertRaises(SystemExit):
            ensure_http_access_token("sse", None)

    def test_stdio_mode_does_not_require_access_token(self):
        from module.mcp_auth import ensure_http_access_token

        self.assertEqual(ensure_http_access_token("stdio", None), "")


if __name__ == "__main__":
    unittest.main()
