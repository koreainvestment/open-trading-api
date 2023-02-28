'''해외선물옵션종목코드 정제 파이썬 파일 : ffcode.mst'''

import pandas as pd
import urllib.request
import ssl
import zipfile
import os

base_dir = os.getcwd()

def get_overseas_future_master_dataframe(base_dir):

    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/ffcode.mst.zip", base_dir + "\\ffcode.mst.zip")
    os.chdir(base_dir)

    nas_zip = zipfile.ZipFile('ffcode.mst.zip')
    nas_zip.extractall()
    nas_zip.close()

    file_name = base_dir + "\\ffcode.mst"
    columns = ['종목코드', '서버자동주문 가능 종목 여부', '서버자동주문 TWAP 가능 종목 여부', '서버자동 경제지표 주문 가능 종목 여부', 
               '필러', '종목한글명', '거래소코드 (ISAM KEY 1)', '품목코드 (ISAM KEY 2)', '품목종류', '출력 소수점', '계산 소수점', 
               '틱사이즈', '틱가치', '계약크기', '가격표시진법', '환산승수', '최다월물여부 0:원월물 1:최다월물', 
               '최근월물여부 0:원월물 1:최근월물', '스프레드여부', '스프레드기준종목 LEG1 여부', '서브 거래소 코드']
    df=pd.DataFrame(columns=columns)
    ridx=1
    print("Downloading...")
    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            a = row[:32]              # 종목코드        
            b = row[32:33].rstrip()   # 서버자동주문 가능 종목 여부
            c = row[33:34].rstrip()   # 서버자동주문 TWAP 가능 종목 여부
            d = row[34:35]            # 서버자동 경제지표 주문 가능 종목 여부  
            e = row[35:82].rstrip()   # 필러
            f = row[82:107].rstrip()  # 종목한글명
            g = row[-92:-82]          # 거래소코드 (ISAM KEY 1)  
            h = row[-82:-72].rstrip() # 품목코드 (ISAM KEY 2)
            i = row[-72:-69].rstrip() # 품목종류
            j = row[-69:-64]          # 출력 소수점  
            k = row[-64:-59].rstrip() # 계산 소수점
            l = row[-59:-45].rstrip() # 틱사이즈
            m = row[-45:-31]          # 틱가치
            n = row[-31:-21].rstrip() # 계약크기 
            o = row[-21:-17].rstrip() # 가격표시진법
            p = row[-17:-7]          # 환산승수
            q = row[-7:-6].rstrip() # 최다월물여부 0:원월물 1:최다월물
            r = row[-6:-5].rstrip() # 최근월물여부 0:원월물 1:최근월물
            s = row[-5:-4].rstrip() # 스프레드여부
            t = row[-4:-3].rstrip() # 스프레드기준종목 LEG1 여부 Y/N
            u = row[-3:].rstrip() # 서브 거래소 코드

            df.loc[ridx] = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u]
            ridx += 1
            
    df.to_excel('ffcode.xlsx',index=False)  # 현재 위치에 엑셀파일로 저장

    return df
    
df = get_overseas_future_master_dataframe(base_dir)
print("Done")
