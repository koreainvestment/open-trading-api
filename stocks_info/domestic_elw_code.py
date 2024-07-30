'''국내ELW 종목정보(elw_code.mst) 정제 파이썬 파일'''

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

def get_elw_master_dataframe(file_path):
    print("Parsing the file...")
    with open(file_path, mode="r", encoding="cp949") as f:
        lines = f.readlines()

    data = []
    for row in lines:
        # print(row)
        mksc_shrn_iscd = row[0:9].strip()                     # 단축코드
        stnd_iscd = row[9:21].strip()                         # 표준코드
        hts_kor_isnm = row[21:50].strip()                     # 한글 종목명
        
        crow = row[50:].strip()
        elw_nvlt_optn_cls_code = crow[:1].strip()             # ELW권리형태
        elw_ko_barrier = crow[1:14].strip()                   # ELW조기종료발생기준가격
        bskt_yn = crow[14:15].strip()                         # 바스켓 여부 (Y/N)
        unas_iscd1 = crow[15:24].strip()                      # 기초자산코드1
        unas_iscd2 = crow[24:33].strip()                      # 기초자산코드2
        unas_iscd3 = crow[33:42].strip()                      # 기초자산코드3
        unas_iscd4 = crow[42:51].strip()                      # 기초자산코드4
        unas_iscd5 = crow[51:60].strip()                      # 기초자산코드5
        
        # Calculate positions from the end of the row
        mrkt_prtt_no10 = row[-6:].strip()                         # 시장 참가자 번호10
        mrkt_prtt_no9 = row[-11:-6].strip()                       # 시장 참가자 번호9
        mrkt_prtt_no8 = row[-16:-11].strip()                      # 시장 참가자 번호8
        mrkt_prtt_no7 = row[-21:-16].strip()                      # 시장 참가자 번호7
        mrkt_prtt_no6 = row[-26:-21].strip()                      # 시장 참가자 번호6
        mrkt_prtt_no5 = row[-31:-26].strip()                      # 시장 참가자 번호5
        mrkt_prtt_no4 = row[-36:-31].strip()                      # 시장 참가자 번호4
        mrkt_prtt_no3 = row[-41:-36].strip()                      # 시장 참가자 번호3
        mrkt_prtt_no2 = row[-46:-41].strip()                      # 시장 참가자 번호2
        mrkt_prtt_no1 = row[-51:-46].strip()                      # 시장 참가자 번호1
        lstn_stcn = row[-66:-51].strip()                          # 상장주수(천)
        prdy_avls = row[-75:-66].strip()                          # 전일시가총액(억)
        paym_date = row[-83:-75].strip()                          # 지급일
        rght_type_cls_code = row[-84:-83].strip()                 # 권리 유형 구분 코드
        rmnn_dynu = row[-88:-84].strip()                          # 잔존 일수
        stck_last_tr_month = row[-96:-88].strip()                 # 최종거래일
        acpr = row[-105:-96].strip()                              # 행사가
        elw_pblc_mrkt_prtt_no = row[-110:-105].strip()            # 발행사코드
        
        elw_pblc_istu_name = row[-11:-110].strip()             # 발행사 한글 종목명
        
        data.append([mksc_shrn_iscd, stnd_iscd, hts_kor_isnm, 
                     elw_nvlt_optn_cls_code, elw_ko_barrier, bskt_yn, 
                     unas_iscd1, unas_iscd2, unas_iscd3, unas_iscd4, 
                     unas_iscd5, elw_pblc_istu_name, elw_pblc_mrkt_prtt_no, 
                     acpr, stck_last_tr_month, rmnn_dynu, rght_type_cls_code, 
                     paym_date, prdy_avls, lstn_stcn, mrkt_prtt_no1,
                     mrkt_prtt_no2, mrkt_prtt_no3, mrkt_prtt_no4, 
                     mrkt_prtt_no5, mrkt_prtt_no6, mrkt_prtt_no7, 
                     mrkt_prtt_no8, mrkt_prtt_no9, mrkt_prtt_no10])

    columns = ['단축코드', '표준코드', '한글종목명', 'ELW권리형태', 'ELW조기종료발생기준가격', 
               '바스켓 여부', '기초자산코드1', '기초자산코드2', '기초자산코드3', 
               '기초자산코드4', '기초자산코드5', '발행사 한글 종목명', '발행사코드', 
               '행사가', '최종거래일', '잔존 일수', '권리 유형 구분 코드', '지급일', 
               '전일시가총액(억)', '상장주수(천)', '시장 참가자 번호1', 
               '시장 참가자 번호2', '시장 참가자 번호3', '시장 참가자 번호4', 
               '시장 참가자 번호5', '시장 참가자 번호6', '시장 참가자 번호7', 
               '시장 참가자 번호8', '시장 참가자 번호9', '시장 참가자 번호10']

    df = pd.DataFrame(data, columns=columns)
    return df

# File details
url = "https://new.real.download.dws.co.kr/common/master/elw_code.mst.zip"
zip_filename = "elw_code.zip"
extracted_filename = "elw_code.mst"

# Download and extract the file
file_path = download_and_extract_file(url, base_dir, zip_filename, extracted_filename)

# Create the DataFrame
df = get_elw_master_dataframe(file_path)

# Save to Excel
print("Saving to Excel...")
df.to_excel('elw_code.xlsx', index=False)
print("Excel file created successfully.")