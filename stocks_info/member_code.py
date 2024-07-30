'''회원사 정보(memcode.mst) 정제 파이썬 파일'''

import pandas as pd
import urllib.request
import ssl
import os

# 현재 작업 디렉토리
base_dir = os.getcwd()

def download_file(url, output_dir, filename):
    # 파일 다운로드
    print(f"Downloading {filename}...")
    ssl._create_default_https_context = ssl._create_unverified_context
    filepath = os.path.join(output_dir, filename)
    urllib.request.urlretrieve(url, filepath)
    return filepath

def parse_memcode_file(file_path):
    
    print("Parsing the file...")
    with open(file_path, mode="r", encoding="cp949") as f:
        lines = f.readlines()

    data = []
    for row in lines:
        if row.strip():  # 빈 줄 제외
            mbcr_no = row[:5].strip()
            mbcr_name = row[5:-2].strip()
            glob_yn = row[-2:].strip()
            data.append([mbcr_no, mbcr_name, glob_yn])

    columns = ['회원사코드', '회원사명', '구분(0=국내, 1=외국)']
    df = pd.DataFrame(data, columns=columns)
    return df

# 회원사 종목코드 마스터파일 다운로드 및 파일 경로
url = "https://new.real.download.dws.co.kr/common/master/memcode.mst"
filename = "memcode.mst"

# 파일 다운로드
file_path = download_file(url, base_dir, filename)

# 데이터프레임 생성
df_memcode = parse_memcode_file(file_path)

# 엑셀 파일로 저장
excel_filename = 'memcode.xlsx'
print("Saving to Excel...")
df_memcode.to_excel(excel_filename, index=False)
print(f"Excel file '{excel_filename}' created successfully.")