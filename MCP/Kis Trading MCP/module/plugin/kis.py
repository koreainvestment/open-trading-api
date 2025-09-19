import logging
import os
import requests


def setup_kis_config(force_update=False):
    """KIS 설정 파일 자동 생성 (템플릿 다운로드 + 환경변수로 값 덮어쓰기)
    
    Args:
        force_update (bool): True면 기존 파일이 있어도 강제로 덮어쓰기
    """

    # kis_auth.py와 동일한 경로 생성 방식 사용
    kis_config_dir = os.path.join(os.path.expanduser("~"), "KIS", "config")

    # KIS 설정 디렉토리 생성
    os.makedirs(kis_config_dir, exist_ok=True)

    # 설정 파일 경로
    kis_config_path = os.path.join(kis_config_dir, "kis_devlp.yaml")

    # 기존 파일 존재 확인
    if os.path.exists(kis_config_path) and not force_update:
        logging.info(f"✅ KIS 설정 파일이 이미 존재합니다: {kis_config_path}")
        logging.info("기존 파일을 사용합니다. 강제 업데이트가 필요한 경우 force_update=True 옵션을 사용하세요.")
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

    # 3. 템플릿 구조를 보존하면서 환경변수 값으로 치환
    updated_content = template_content
    
    # 환경변수 값이 있으면 해당 필드만 업데이트
    if app_key:
        updated_content = updated_content.replace('my_app: "앱키"', f'my_app: "{app_key}"')
    if app_secret:
        updated_content = updated_content.replace('my_sec: "앱키 시크릿"', f'my_sec: "{app_secret}"')
    
    if paper_app_key:
        updated_content = updated_content.replace('paper_app: "모의투자 앱키"', f'paper_app: "{paper_app_key}"')
    if paper_app_secret:
        updated_content = updated_content.replace('paper_sec: "모의투자 앱키 시크릿"', f'paper_sec: "{paper_app_secret}"')
    
    if hts_id:
        updated_content = updated_content.replace('my_htsid: "사용자 HTS ID"', f'my_htsid: "{hts_id}"')
    
    if acct_stock:
        updated_content = updated_content.replace('my_acct_stock: "증권계좌 8자리"', f'my_acct_stock: "{acct_stock}"')
    if acct_future:
        updated_content = updated_content.replace('my_acct_future: "선물옵션계좌 8자리"', f'my_acct_future: "{acct_future}"')
    if paper_stock:
        updated_content = updated_content.replace('my_paper_stock: "모의투자 증권계좌 8자리"', f'my_paper_stock: "{paper_stock}"')
    if paper_future:
        updated_content = updated_content.replace('my_paper_future: "모의투자 선물옵션계좌 8자리"', f'my_paper_future: "{paper_future}"')
    
    if prod_type != "01":  # 기본값이 아닌 경우만 업데이트
        updated_content = updated_content.replace('my_prod: "01"', f'my_prod: "{prod_type}"')
    
    # URL 설정 업데이트
    if url_rest:
        updated_content = updated_content.replace('prod: "https://openapi.koreainvestment.com:9443"', f'prod: "{url_rest}"')
    if url_rest_paper:
        updated_content = updated_content.replace('vps: "https://openapivts.koreainvestment.com:29443"', f'vps: "{url_rest_paper}"')
    if url_ws:
        updated_content = updated_content.replace('ops: "ws://ops.koreainvestment.com:21000"', f'ops: "{url_ws}"')
    if url_ws_paper:
        updated_content = updated_content.replace('vops: "ws://ops.koreainvestment.com:31000"', f'vops: "{url_ws_paper}"')

    # 4. 수정된 설정을 파일로 저장 (원본 구조 보존)
    try:
        with open(kis_config_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

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
