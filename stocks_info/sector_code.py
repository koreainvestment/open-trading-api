import pandas as pd
import urllib.request
import ssl
import zipfile


def get_theme_master_dataframe():
    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/idxcode.mst.zip",
                               "idxcode.zip")

    kospi_zip = zipfile.ZipFile('idxcode.zip')
    kospi_zip.extractall()
    kospi_zip.close()

    file_name = "idxcode.mst"
    df = pd.DataFrame(columns=['업종코드', '업종명'])

    ridx = 1
    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            tcode = row[0:5]  # 업종코드
            tname = row[3:43].rstrip()  # 업종명
            df.loc[ridx] = [tcode, tname]

            ridx += 1

    return df


df = get_theme_master_dataframe()  # pysam 임시폴더 사용
