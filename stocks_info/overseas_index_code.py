'''
* 해외주식지수정보(frgn_code.mst) 정제 파이썬 파일
* 정제완료된 엑셀파일 : frgn_code.xlsx
* overseas_index_code.py(frgn_code.mst)은 해외지수 정보 제공용으로 개발된 파일로
  해외주식 정보에 대해 얻고자 할 경우 overseas_stock_code.py(ex. nasmst.cod) 이용하시기 바랍니다.
'''

import pandas as pd
import urllib.request
import ssl
import zipfile
import os
import numpy as np

base_dir = os.getcwd()

def get_overseas_index_master_dataframe(base_dir):

    # download file
    print("Downloading...")
    
    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/frgn_code.mst.zip", base_dir + "\\frgn_code.mst.zip")
    os.chdir(base_dir)

    frgn_code_zip = zipfile.ZipFile('frgn_code.mst.zip')
    frgn_code_zip.extractall()
    frgn_code_zip.close()
    file_name = base_dir + "\\frgn_code.mst"

    # df1 : '구분코드','심볼','영문명','한글명'
    tmp_fil1 = base_dir + "\\frgn_code_part1.tmp"
    tmp_fil2 = base_dir + "\\frgn_code_part2.tmp"
    wf1 = open(tmp_fil1, mode="w")
    wf2 = open(tmp_fil2, mode="w")
    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            if row[0:1] == 'X':
                rf1 = row[0:len(row) - 14]
                rf_1 = rf1[0:1]
                rf1_2 = rf1[1:11]
                rf1_3 = rf1[11:40].replace(",","")
                rf1_4 = rf1[40:80].replace(",","").strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + ',' + rf1_4 + '\n')
                rf2 = row[-15:]
                wf2.write(rf2+'\n')
                continue
            rf1 = row[0:len(row) - 14]
            rf1_1 = rf1[0:1]
            rf1_2 = rf1[1:11]
            rf1_3 = rf1[11:50].replace(",","")
            rf1_4 = row[50:75].replace(",","").strip()
            wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + ',' + rf1_4 + '\n')
            rf2 = row[-15:]
            wf2.write(rf2+'\n')
    wf1.close()
    wf2.close()
    part1_columns = ['구분코드','심볼','영문명','한글명']
    df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')

    # df2 : '종목업종코드','다우30 편입종목여부','나스닥100 편입종목여부', 'S&P 500 편입종목여부','거래소코드','국가구분코드'
    
    field_specs = [4, 1, 1, 1, 4, 3]
    part2_columns = ['종목업종코드','다우30 편입종목여부','나스닥100 편입종목여부',
                     'S&P 500 편입종목여부','거래소코드','국가구분코드']
    df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns, encoding='cp949')
    
    df2['종목업종코드'] = df2['종목업종코드'].str.replace(pat=r'[^A-Z]', repl= r'', regex=True) # 종목업종코드는 잘못 기입되어 있을 수 있으니 참고할 때 반드시 mst 파일과 비교 참고
    df2['다우30 편입종목여부'] = df2['다우30 편입종목여부'].str.replace(pat=r'[^0-1]+', repl= r'', regex=True) # 한글명 길이가 길어서 생긴 오타들 제거
    df2['나스닥100 편입종목여부'] = df2['나스닥100 편입종목여부'].str.replace(pat=r'[^0-1]+', repl= r'', regex=True)
    df2['S&P 500 편입종목여부'] = df2['S&P 500 편입종목여부'].str.replace(pat=r'[^0-1]+', repl= r'', regex=True)

    # DF : df1 + df2
    DF = pd.concat([df1,df2],axis=1)
    # print(len(df1), len(df2), len(DF))
    DF.to_excel('frgn_code.xlsx',index=False)  # 현재 위치에 엑셀파일로 저장
    
    return DF

df = get_overseas_index_master_dataframe(base_dir)
print("Done")
