'''코넥스주식 종목정보(konex_code.mst) 정제 파이썬 파일'''

import pandas as pd
import urllib.request
import ssl
import zipfile
import os

base_dir = os.getcwd()

def download_and_extract_file(url, output_dir, zip_filename, extracted_filename):
    # Download the file
    print(f"Downloading {zip_filename}...")
    ssl._create_default_https_context = ssl._create_unverified_context
    zip_filepath = os.path.join(output_dir, zip_filename)
    urllib.request.urlretrieve(url, zip_filepath)
    
    # Extract the file
    print(f"Extracting {zip_filename}...")
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    return os.path.join(output_dir, extracted_filename)

def get_knx_master_dataframe(file_path):
    print("Parsing the file...")
    with open(file_path, mode="r", encoding="cp949") as f:
        lines = f.readlines()

    data = []
    for row in lines:
        row = row.strip()
        mksc_shrn_iscd = row[0:9].strip()
        stnd_iscd = row[9:21].strip()
        scrt_grp_cls_code = row[-184:-182].strip()
        stck_sdpr = row[-182:-173].strip()
        frml_mrkt_deal_qty_unit = row[-173:-168].strip()
        ovtm_mrkt_deal_qty_unit = row[-168:-163].strip()
        trht_yn = row[-163:-162].strip()
        sltr_yn = row[-162:-161].strip()
        mang_issu_yn = row[-161:-160].strip()
        mrkt_alrm_cls_code = row[-160:-158].strip()
        mrkt_alrm_risk_adnt_yn = row[-158:-157].strip()
        insn_pbnt_yn = row[-157:-156].strip()
        byps_lstn_yn = row[-156:-155].strip()
        flng_cls_code = row[-155:-153].strip()
        fcam_mod_cls_code = row[-153:-151].strip()
        icic_cls_code = row[-151:-149].strip()
        marg_rate = row[-149:-146].strip()
        crdt_able = row[-146:-145].strip()
        crdt_days = row[-145:-142].strip()
        prdy_vol = row[-142:-130].strip()
        stck_fcam = row[-130:-118].strip()
        stck_lstn_date = row[-118:-110].strip()
        lstn_stcn = row[-110:-95].strip()
        cpfn = row[-95:-74].strip()
        stac_month = row[-74:-72].strip()
        po_prc = row[-72:-65].strip()
        prst_cls_code = row[-65:-64].strip()
        ssts_hot_yn = row[-64:-63].strip()
        stange_runup_yn = row[-63:-62].strip()
        krx300_issu_yn = row[-62:-61].strip()
        sale_account = row[-61:-52].strip()
        bsop_prfi = row[-52:-43].strip()
        op_prfi = row[-43:-34].strip()
        thtr_ntin = row[-34:-29].strip()
        roe = row[-29:-20].strip()
        base_date = row[-20:-12].strip()
        prdy_avls_scal = row[-12:-3].strip()
        co_crdt_limt_over_yn = row[-3:-2].strip()
        secu_lend_able_yn = row[-2:-1].strip()
        stln_able_yn = row[-1:].strip()
        hts_kor_isnm = row[21:-184].strip()

        data.append([mksc_shrn_iscd, stnd_iscd, hts_kor_isnm, scrt_grp_cls_code, 
                     stck_sdpr, frml_mrkt_deal_qty_unit, ovtm_mrkt_deal_qty_unit, 
                     trht_yn, sltr_yn, mang_issu_yn, mrkt_alrm_cls_code, 
                     mrkt_alrm_risk_adnt_yn, insn_pbnt_yn, byps_lstn_yn, 
                     flng_cls_code, fcam_mod_cls_code, icic_cls_code, marg_rate, 
                     crdt_able, crdt_days, prdy_vol, stck_fcam, stck_lstn_date, 
                     lstn_stcn, cpfn, stac_month, po_prc, prst_cls_code, ssts_hot_yn, 
                     stange_runup_yn, krx300_issu_yn, sale_account, bsop_prfi, 
                     op_prfi, thtr_ntin, roe, base_date, prdy_avls_scal, 
                     co_crdt_limt_over_yn, secu_lend_able_yn, stln_able_yn])

    columns = ['단축코드', '표준코드', '종목명', '증권그룹구분코드', '주식 기준가', 
               '정규 시장 매매 수량 단위', '시간외 시장 매매 수량 단위', '거래정지 여부', 
               '정리매매 여부', '관리 종목 여부', '시장 경고 구분 코드', '시장 경고위험 예고 여부', 
               '불성실 공시 여부', '우회 상장 여부', '락구분 코드', '액면가 변경 구분 코드', 
               '증자 구분 코드', '증거금 비율', '신용주문 가능 여부', '신용기간', '전일 거래량', 
               '주식 액면가', '주식 상장 일자', '상장 주수(천)', '자본금', '결산 월', '공모 가격', 
               '우선주 구분 코드', '공매도과열종목여부', '이상급등종목여부', 'KRX300 종목 여부', 
               '매출액', '영업이익', '경상이익', '단기순이익', 'ROE', '기준년월', '전일기준 시가총액(억)', 
               '회사신용한도초과여부', '담보대출가능여부', '대주가능여부']

    df = pd.DataFrame(data, columns=columns)
    return df

# 코넥스 종목코드 마스터파일 다운로드 및 파일 경로
url = "https://new.real.download.dws.co.kr/common/master/konex_code.mst.zip"
zip_filename = "konex_code.zip"
extracted_filename = "konex_code.mst"

file_path = download_and_extract_file(url, base_dir, zip_filename, extracted_filename)

# 데이터프레임 생성 및 엑셀 파일로 저장
df_knx = get_knx_master_dataframe(file_path)

# 엑셀 파일 저장
print("Saving to Excel...")
df_knx.to_excel('konex_code.xlsx', index=False)
print("Excel file created successfully.")