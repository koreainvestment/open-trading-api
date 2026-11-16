import logging
import os
import shutil
import tempfile

import requests
import yaml


def _yaml_dq(value):
    """YAML 큰따옴표 스칼라용 이스케이프 (폴백 치환 경로에서 사용)."""
    return (value or "").replace("\\", "\\\\").replace('"', '\\"')


def setup_kis_config(force_update=False):
    """KIS 설정 파일 자동 생성 (템플릿 다운로드 + 환경변수로 값 덮어쓰기)

    기존 파일은 기본적으로 보존한다. 덮어쓰기는 force_update=True에 더해
    MCP_KIS_CONFIG_OVERWRITE=1 명시 옵트인이 있을 때만 수행하고, 그 경우에도
    필수 환경변수(KIS_APP_KEY/KIS_APP_SECRET)가 모두 있을 때만 갱신한다.
    덮어쓰기 전 kis_devlp.yaml.bak에 백업하고, 새 파일은 0600·원자적 저장이다.

    Args:
        force_update (bool): True여도 옵트인 없이는 기존 파일을 덮어쓰지 않음
    """

    # kis_auth.py와 동일한 경로 생성 방식 사용
    kis_config_dir = os.path.join(os.path.expanduser("~"), "KIS", "config")

    # KIS 설정 디렉토리 생성
    os.makedirs(kis_config_dir, exist_ok=True)

    # 설정 파일 경로
    kis_config_path = os.path.join(kis_config_dir, "kis_devlp.yaml")
    existed = os.path.exists(kis_config_path)

    # 기존 파일 존재 확인: 기본 보존, 명시 옵트인 때만 갱신 대상으로 둔다
    if existed and not (force_update
                        and (os.getenv("MCP_KIS_CONFIG_OVERWRITE") or "") == "1"):
        logging.info(f"✅ KIS 설정 파일이 이미 존재합니다: {kis_config_path}")
        logging.info("기존 파일을 보존합니다. 덮어쓰려면 force_update=True와 "
                     "MCP_KIS_CONFIG_OVERWRITE=1이 모두 필요합니다.")
        return True

    # 1. kis_devlp.yaml 템플릿 다운로드
    template_url = "https://raw.githubusercontent.com/koreainvestment/open-trading-api/refs/heads/main/kis_devlp.yaml"

    try:
        logging.info("KIS 설정 템플릿을 다운로드 중...")
        response = requests.get(template_url, timeout=30)
        response.raise_for_status()

        # 원본 템플릿 텍스트 보존
        template_content = response.text
        logging.info("✅ KIS 설정 템플릿 다운로드 완료")

    except Exception as e:
        logging.error(f"❌ KIS 설정 템플릿 다운로드 실패: {e}")
        return False

    # 2. 환경변수로 민감한 정보 덮어쓰기
    # 필수값 (누락 시 경고)
    app_key = os.getenv("KIS_APP_KEY")
    app_secret = os.getenv("KIS_APP_SECRET")

    if not app_key or not app_secret:
        if existed:
            logging.error("❌ 필수 환경변수(KIS_APP_KEY/KIS_APP_SECRET)가 없어 "
                          "기존 설정 파일을 보존합니다. 덮어쓰지 않았습니다.")
            return False
        logging.warning("⚠️ 필수 환경변수가 설정되지 않았습니다:")
        if not app_key:
            logging.warning("  - KIS_APP_KEY")
        if not app_secret:
            logging.warning("  - KIS_APP_SECRET")
        logging.warning("실제 거래 API 사용이 불가능할 수 있습니다.")

    # 선택적 값들 (누락 시 빈값 또는 기본값)
    paper_app_key = os.getenv("KIS_PAPER_APP_KEY", "")
    paper_app_secret = os.getenv("KIS_PAPER_APP_SECRET", "")
    hts_id = os.getenv("KIS_HTS_ID", "")
    acct_stock = os.getenv("KIS_ACCT_STOCK", "")
    acct_future = os.getenv("KIS_ACCT_FUTURE", "")
    paper_stock = os.getenv("KIS_PAPER_STOCK", "")
    paper_future = os.getenv("KIS_PAPER_FUTURE", "")
    prod_type = os.getenv("KIS_PROD_TYPE", "01")  # 기본값: 종합계좌
    url_rest = os.getenv("KIS_URL_REST", "")
    url_rest_paper = os.getenv("KIS_URL_REST_PAPER", "")
    url_ws = os.getenv("KIS_URL_WS", "")
    url_ws_paper = os.getenv("KIS_URL_WS_PAPER", "")

    # 3. YAML 파싱하여 값 업데이트
    try:
        # YAML 파싱 (주석 보존을 위해 ruamel.yaml 사용하거나, 간단히 pyyaml 사용)
        config = yaml.safe_load(template_content)

        # 환경변수 값이 있으면 해당 필드만 업데이트
        if app_key:
            config['my_app'] = app_key
            logging.info(f"✅ 실전 App Key 설정 완료")
        if app_secret:
            config['my_sec'] = app_secret
            logging.info(f"✅ 실전 App Secret 설정 완료")

        if paper_app_key:
            config['paper_app'] = paper_app_key
            logging.info(f"✅ 모의 App Key 설정 완료")
        if paper_app_secret:
            config['paper_sec'] = paper_app_secret
            logging.info(f"✅ 모의 App Secret 설정 완료")

        if hts_id:
            config['my_htsid'] = hts_id
            logging.info("✅ HTS ID 설정 완료")
        else:
            logging.warning("⚠️ KIS_HTS_ID 환경변수가 설정되지 않았습니다.")

        if acct_stock:
            config['my_acct_stock'] = acct_stock
            logging.info(f"✅ 증권계좌 설정 완료")
        if acct_future:
            config['my_acct_future'] = acct_future
            logging.info(f"✅ 선물옵션계좌 설정 완료")
        if paper_stock:
            config['my_paper_stock'] = paper_stock
            logging.info(f"✅ 모의 증권계좌 설정 완료")
        if paper_future:
            config['my_paper_future'] = paper_future
            logging.info(f"✅ 모의 선물옵션계좌 설정 완료")

        if prod_type != "01":  # 기본값이 아닌 경우만 업데이트
            config['my_prod'] = prod_type
            logging.info(f"✅ 계좌상품코드 설정 완료: {prod_type}")

        # URL 설정 업데이트 (직접 필드)
        if url_rest:
            config['prod'] = url_rest
            logging.info(f"✅ 실전 REST URL 설정 완료")
        if url_rest_paper:
            config['vps'] = url_rest_paper
            logging.info(f"✅ 모의 REST URL 설정 완료")
        if url_ws:
            config['ops'] = url_ws
            logging.info(f"✅ 실전 WebSocket URL 설정 완료")
        if url_ws_paper:
            config['vops'] = url_ws_paper
            logging.info(f"✅ 모의 WebSocket URL 설정 완료")

        # YAML로 다시 변환
        updated_content = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)

    except yaml.YAMLError as e:
        logging.error(f"❌ YAML 파싱 오류: {e}")
        logging.info("문자열 치환 방식으로 대체합니다...")
        # 실패 시 기존 문자열 치환 방식 사용
        updated_content = template_content
        if app_key:
            updated_content = updated_content.replace('my_app: "앱키"', f'my_app: "{_yaml_dq(app_key)}"')
        if app_secret:
            updated_content = updated_content.replace('my_sec: "앱키 시크릿"', f'my_sec: "{_yaml_dq(app_secret)}"')
        if hts_id:
            updated_content = updated_content.replace('my_htsid: "사용자 HTS ID"', f'my_htsid: "{_yaml_dq(hts_id)}"')
        # ... 나머지 기존 로직

    # 4. 수정된 설정을 파일로 저장 (기존 파일은 .bak 백업 후 0600 원자적 저장)
    if existed:
        try:
            shutil.copyfile(kis_config_path, kis_config_path + ".bak")
            logging.info(f"💾 기존 설정 백업: {kis_config_path}.bak")
        except Exception as e:
            logging.error(f"❌ 백업 실패로 덮어쓰기를 중단합니다: {e}")
            return False
    try:
        fd, tmp_path = tempfile.mkstemp(dir=kis_config_dir, prefix=".kis_devlp_")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(updated_content)
            os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, kis_config_path)
            try:
                os.chmod(kis_config_path, 0o600)
            except OSError:
                pass
        except BaseException:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

        logging.info(f"✅ KIS 설정 파일이 생성되었습니다: {kis_config_path}")

        # 설정 요약 출력
        logging.info("📋 KIS 설정 요약:")
        logging.info(f"  - 실제 거래: {'✅' if app_key and app_secret else '❌'}")
        logging.info(f"  - 모의 거래: {'✅' if paper_app_key and paper_app_secret else '❌'}")
        logging.info(f"  - 계좌번호: {'✅' if any([acct_stock, acct_future, paper_stock, paper_future]) else '❌'}")
        logging.info(f"  - URL 설정: {'✅' if any([url_rest, url_rest_paper, url_ws, url_ws_paper]) else '❌'}")

        return True

    except Exception as e:
        logging.error(f"❌ KIS 설정 파일 생성 실패: {e}")
        return False
