import logging
import os
from collections import namedtuple

from dotenv import load_dotenv

# Environment 설정을 위한 namedtuple 정의
EnvironmentConfig = namedtuple('EnvironmentConfig', [
    'mcp_type', 'mcp_host', 'mcp_port', 'mcp_path'
])


def setup_environment(env: str) -> EnvironmentConfig:
    # get api env
    if not env:
        logging.error("Environment variable ENV not defined")
        exit(1)

    # load .env
    dotenv_path = os.path.join(os.getcwd(), f".env.{env}")
    if not os.path.isfile(dotenv_path):
        logging.error(f"Environment variable file .env.{env} not found")
        exit(1)

    load_dotenv(dotenv_path=dotenv_path)

    # return environment
    # MCP_TYPE 검증 및 기본값 설정
    mcp_type = os.getenv("MCP_TYPE", "stdio")
    if mcp_type not in ['stdio', 'sse', 'streamable-http']:
        logging.warning(f"Invalid MCP_TYPE: {mcp_type}, using default: stdio")
        mcp_type = "stdio"

    # MCP_PORT가 빈 문자열이면 기본값 사용
    mcp_port_str = os.getenv("MCP_PORT", "8000")
    mcp_port = int(mcp_port_str) if mcp_port_str.strip() else 8000

    return EnvironmentConfig(
        mcp_type=mcp_type,
        mcp_host=os.getenv("MCP_HOST", "localhost"),
        mcp_port=mcp_port,
        mcp_path=os.getenv("MCP_PATH", "/mcp")
    )
