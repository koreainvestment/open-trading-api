import pandas as pd
import urllib.request
import ssl
import zipfile
import os

base_dir = os.getcwd()

def get_theme_master_dataframe(base_dir):

    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/theme_code.mst.zip", base_dir + "\\theme_code.zip")
    os.chdir(base_dir)

    kospi_zip = zipfile.ZipFile('theme_code.zip')
    kospi_zip.extractall()
    kospi_zip.close()

    file_name = base_dir + "\\theme_code.mst"
    df = pd.DataFrame(columns = ['테마코드', '테마명', '종목코드'])

    ridx = 1
    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            tcode = row[0:3]            # 테마코드
            jcode = row[-10:].rstrip()  # 테마명
            tname = row[3:-10].rstrip() # 종목코드
            df.loc[ridx] = [tcode, tname, jcode]
            # print(df.loc[ridx])  # 파일 작성중인 것을 확인할 수 있음
            ridx += 1

    return df

df1 = get_theme_master_dataframe(base_dir)
df1.to_excel('theme_code.xlsx',index=False)  # 현재 위치에 엑셀파일로 저장
df1