'''상품선물옵션 종목코드(fo_com_code_mts.mst) 정제 파이썬 파일'''

import pandas as pd
import urllib.request
import ssl
import zipfile
import os

base_dir = os.getcwd()

def get_domestic_com_future_master_dataframe(base_dir):
    
    # download file
    print("Downloading...")

    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/fo_com_code.mst.zip", base_dir + "\\fo_com_code.mst.zip")
    os.chdir(base_dir)

    fo_com_code_zip = zipfile.ZipFile('fo_com_code.mst.zip')
    fo_com_code_zip.extractall()
    fo_com_code_zip.close()
    file_name = base_dir + "\\fo_com_code.mst"

    # df1 : '상품구분','상품종류','단축코드','표준코드','한글종목명'
    tmp_fil1 = base_dir + "\\fo_com_code_part1.tmp"
    tmp_fil2 = base_dir + "\\fo_com_code_part2.tmp"
    wf1 = open(tmp_fil1, mode="w")
    wf2 = open(tmp_fil2, mode="w")
    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            rf1 = row[0:55]
            rf1_1 = rf1[0:1]
            rf1_2 = rf1[1:2]
            rf1_3 = rf1[2:11].strip()
            rf1_4 = rf1[11:23].strip()
            rf1_5 = rf1[23:55].strip()
            wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + ',' + rf1_4 + ',' + rf1_5 + '\n')
            rf2 = row[55:].lstrip()
            wf2.write(rf2)
    wf1.close()
    wf2.close()
    part1_columns = ['상품구분','상품종류','단축코드','표준코드','한글종목명']
    df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')

    # df2 : '월물구분코드','기초자산 단축코드','기초자산 명'
    tmp_fil3 = base_dir + "\\fo_com_code_part3.tmp"
    wf3 = open(tmp_fil3, mode="w")
    with open(tmp_fil2, mode="r", encoding="cp949") as f:
        for row in f:
            rf2 = row[:]
            rf2_1 = rf2[8:9]
            rf2_2 = rf2[9:12]
            rf2_3 = rf2[12:].strip()
            wf3.write(rf2_1 + ',' + rf2_2 + ',' + rf2_3 + '\n')
    wf3.close()
    part2_columns = ['월물구분코드','기초자산 단축코드','기초자산 명']
    df2 = pd.read_csv(tmp_fil3, header=None, names=part2_columns, encoding='cp949')

    # DF : df1 + df2
    DF = pd.concat([df1,df2],axis=1)
    # print(len(df1), len(df2), len(DF))
    DF.to_excel('fo_com_code.xlsx',index=False)  # 현재 위치에 엑셀파일로 저장
    
    return DF

df = get_domestic_com_future_master_dataframe(base_dir)
print("Done")