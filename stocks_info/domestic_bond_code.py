'''장내채권 종목정보(bond_code.mst) 정제 파이썬 파일'''

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

def get_bond_master_dataframe(file_path):
    print("Parsing the file...")
    with open(file_path, mode="r", encoding="cp949") as f:
        lines = f.readlines()

    data = []
    for row in lines:
        row = row.strip()
        bond_type = row[0:2].strip()
        bond_cls_code = row[2:4].strip()
        stnd_iscd = row[4:16].strip()
        rdmp_date = row[-8:].strip()
        pblc_date = row[-16:-8].strip()
        lstn_date = row[-24:-16].strip()
        bond_int_cls_code = row[-26:-24].strip()
        sname = row[16:-26].rstrip()  # 종목명을 뒤에서부터 추출하여 남은 부분

        data.append([bond_type, bond_cls_code, stnd_iscd, sname, bond_int_cls_code, 
                     lstn_date, pblc_date, rdmp_date])

    columns = ['유형', '채권분류코드', '표준코드', '종목명', '채권이자분류코드', 
               '상장일', '발행일', '상환일']

    df = pd.DataFrame(data, columns=columns)
    return df

# 채권종목코드 마스터파일 다운로드 및 파일 경로
url = "https://new.real.download.dws.co.kr/common/master/bond_code.mst.zip"
zip_filename = "bond_code.zip"
extracted_filename = "bond_code.mst"

file_path = download_and_extract_file(url, base_dir, zip_filename, extracted_filename)

# 데이터프레임 생성 및 엑셀 파일로 저장
df_bond = get_bond_master_dataframe(file_path)

# 엑셀 파일 저장
print("Saving to Excel...")
df_bond.to_excel('bond_code.xlsx', index=False)
print("Excel file created successfully.")