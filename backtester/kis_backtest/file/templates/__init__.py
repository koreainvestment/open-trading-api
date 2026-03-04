"""Strategy File Templates.

샘플 전략 파일들을 제공합니다.
"""

from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent


def get_template_path(name: str) -> Path:
    """템플릿 파일 경로 반환"""
    path = TEMPLATES_DIR / f"{name}.kis.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {name}")
    return path


def list_templates() -> list[str]:
    """사용 가능한 템플릿 목록"""
    return [p.stem.replace(".kis", "") for p in TEMPLATES_DIR.glob("*.kis.yaml")]
