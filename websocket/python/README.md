
https://www.python.org/downloads/windows/
python-3.10.1-amd64

install 버전으로 다운받아 설치하고 설치 첫 화면에서 path 설정도 체크를 해 준다.

# pip 버전확인 (21.3.1이 아닐경우 plugin 설치가 되지않을수 있음)
D:\>pip -V
pip 21.3.1 from C:\Users\neogram03\AppData\Local\Programs\Python\Python310\lib\site-packages\pip (python 3.10)

# pip 업데이트 커맨드 (관리자모드command prompt 에서 실행)
> pip install --upgrade pip


# python websocket 사용을 위해 다음을 설치해야합니다.
> pip install websockets
Collecting websockets
Installing collected packages: websockets
Successfully installed websockets-10.1

# python aes256 사용을 위해 다음을 설치해야 합니다.
> pip install pycryptodome 

# 테스트(실행) 방법, 실행은 관리자모드가 아닌 command prompt에서 실행한다
> python ops_websocket_sample.py

# 테스트시 app 키를 변경해야 할 경우 113라인을 수정한다.
# 테스트시 종목명을 변경해야 할 경우 116라인을 수정한다.
# 테스트시 htsid 를 변경해야 할 경우 117라인을 수정한다.

