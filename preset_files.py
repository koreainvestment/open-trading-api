import os
import shutil

if not os.path.exists("info"):
    os.mkdir("info")

# stock_info directory exist check
if not os.path.exists("pysam"):
    os.mkdir("pysam")

os.chdir("pysam")

# file write
with open(".ignore", mode="w", encoding="UTF-8") as f:
    f.write("*")

from stocks_info import kis_kospi_code_mst, sector_code, theme_code

os.chdir("..")
kis_kospi_code_mst.df.to_csv('info/kospi_code.csv', encoding='utf-8', index=False)
sector_code.df.to_csv("info/sector_code.csv", encoding="UTF-8", index=False)
theme_code.df.to_csv('info/theme_code.csv', encoding='utf-8', index=False)
# pipenv run pip3 freeze > requirements.txt
