'''CME연계 야간선물 종목코드(fo_cme_code.mst) 정제 파이썬 파일'''

import pandas as pd
import urllib.request
import ssl
import zipfile
import os

base_dir = os.getcwd()

def get_domestic_cme_future_master_dataframe(base_dir):
    
    # download file
    print("Downloading...")

    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/fo_cme_code.mst.zip", base_dir + "\\fo_cme_code.mst.zip")
    os.chdir(base_dir)

    fo_cme_code_zip = zipfile.ZipFile('fo_cme_code.mst.zip')
    fo_cme_code_zip.extractall()
    fo_cme_code_zip.close()
    file_name = base_dir + "\\fo_cme_code.mst"
    columns = ['상품종류','단축코드','표준코드',' 한글종목명',
               '행사가',' 기초자산 단축코드',' 기초자산 명']
    df=pd.DataFrame(columns=columns)
    ridx=1
    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            a = row[0:1]
            b = row[1:10].strip()
            c = row[10:22].strip()
            d = row[22:63].strip()
            e = row[63:72].strip()
            f = row[72:81].strip()
            g = row[81:].strip()
            df.loc[ridx] = [a,b,c,d,e,f,g]
            ridx += 1
    df.to_excel('fo_cme_code.xlsx',index=False)  # 현재 위치에 엑셀파일로 저장
    
    return df

df = get_domestic_cme_future_master_dataframe(base_dir)
print("Done")