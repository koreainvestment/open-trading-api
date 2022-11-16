'''코스피주식종목코드(kospi_code.mst) 정제 파이썬 파일'''

import urllib.request
import ssl
import zipfile
import os
import pandas as pd

base_dir = os.getcwd()

def kospi_master_download(base_dir, verbose=False):
    cwd = os.getcwd()
    if (verbose): print(f"current directory is {cwd}")
    ssl._create_default_https_context = ssl._create_unverified_context

    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
                               base_dir + "\\kospi_code.zip")

    os.chdir(base_dir)
    if (verbose): print(f"change directory to {base_dir}")
    kospi_zip = zipfile.ZipFile('kospi_code.zip')
    kospi_zip.extractall()

    kospi_zip.close()

    if os.path.exists("kospi_code.zip"):
        os.remove("kospi_code.zip")


def get_kospi_master_dataframe(base_dir):
    file_name = base_dir + "\\kospi_code.mst"
    tmp_fil1 = base_dir + "\\kospi_code_part1.tmp"
    tmp_fil2 = base_dir + "\\kospi_code_part2.tmp"

    wf1 = open(tmp_fil1, mode="w")
    wf2 = open(tmp_fil2, mode="w")

    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            rf1 = row[0:len(row) - 228]
            rf1_1 = rf1[0:9].rstrip()
            rf1_2 = rf1[9:21].rstrip()
            rf1_3 = rf1[21:].strip()
            wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
            rf2 = row[-228:]
            wf2.write(rf2)

    wf1.close()
    wf2.close()

    part1_columns = ['단축코드', '표준코드', '한글명']
    df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')

    field_specs = [2, 1, 4, 4, 4,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 9, 5, 5, 1,
                   1, 1, 2, 1, 1,
                   1, 2, 2, 2, 3,
                   1, 3, 12, 12, 8,
                   15, 21, 2, 7, 1,
                   1, 1, 1, 1, 9,
                   9, 9, 5, 9, 8,
                   9, 3, 1, 1, 1
                   ]

    part2_columns = ['그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류',
                     '제조업', '저유동성', '지배구조지수종목', 'KOSPI200섹터업종', 'KOSPI100',
                     'KOSPI50', 'KRX', 'ETP', 'ELW발행', 'KRX100',
                     'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC',
                     'KRX에너지화학', 'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설',
                     'Non1', 'KRX증권', 'KRX선박', 'KRX섹터_보험', 'KRX섹터_운송',
                     'SRI', '기준가', '매매수량단위', '시간외수량단위', '거래정지',
                     '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시',
                     '우회상장', '락구분', '액면변경', '증자구분', '증거금비율',
                     '신용가능', '신용기간', '전일거래량', '액면가', '상장일자',
                     '상장주수', '자본금', '결산월', '공모가', '우선주',
                     '공매도과열', '이상급등', 'KRX300', 'KOSPI', '매출액',
                     '영업이익', '경상이익', '당기순이익', 'ROE', '기준년월',
                     '시가총액', '그룹사코드', '회사신용한도초과', '담보대출가능', '대주가능'
                     ]

    df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)

    df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

    # clean temporary file and dataframe
    del (df1)
    del (df2)
    os.remove(tmp_fil1)
    os.remove(tmp_fil2)
    
    print("Done")

    return df


kospi_master_download(base_dir)
df = get_kospi_master_dataframe(base_dir) 

#df3 = df[df['KRX증권'] == 'Y']
df3 = df
# print(df3[['단축코드', '한글명', 'KRX', 'KRX증권', '기준가', '증거금비율', '상장일자', 'ROE']])
df3.to_excel('kospi_code.xlsx',index=False) # 현재 위치에 엑셀파일로 저장
df3
