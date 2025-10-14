import asyncio
import websockets
import json
import time
from multiprocessing import Process, Queue, Manager
import json
import time
import requests
import asyncio
import websockets
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 웹소켓 접속키 발급
def get_approval(key, secret):
    
    # url = https://openapivts.koreainvestment.com:29443' # 모의투자계좌     
    url = 'https://openapi.koreainvestment.com:9443' # 실전투자계좌
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": key,
            "secretkey": secret}
    PATH = "oauth2/Approval"
    URL = f"{url}/{PATH}"
    time.sleep(0.05)
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    approval_key = res.json()["approval_key"]
    return approval_key


# 국내주식호가 출력라이브러리
def stockhoka(data):
    """ 넘겨받는데이터가 정상인지 확인
    print("stockhoka[%s]"%(data))
    """
    recvvalue = data.split('^')  # 수신데이터를 split '^'

"""
    print("유가증권 단축 종목코드 [" + recvvalue[0] + "]")
    print("영업시간 [" + recvvalue[1] + "]" + "시간구분코드 [" + recvvalue[2] + "]")
    print("======================================")
    print("매도호가10 [%s]    잔량10 [%s]" % (recvvalue[12], recvvalue[32]))
    print("매도호가09 [%s]    잔량09 [%s]" % (recvvalue[11], recvvalue[31]))
    print("매도호가08 [%s]    잔량08 [%s]" % (recvvalue[10], recvvalue[30]))
    print("매도호가07 [%s]    잔량07 [%s]" % (recvvalue[9], recvvalue[29]))
    print("매도호가06 [%s]    잔량06 [%s]" % (recvvalue[8], recvvalue[28]))
    print("매도호가05 [%s]    잔량05 [%s]" % (recvvalue[7], recvvalue[27]))
    print("매도호가04 [%s]    잔량04 [%s]" % (recvvalue[6], recvvalue[26]))
    print("매도호가03 [%s]    잔량03 [%s]" % (recvvalue[5], recvvalue[25]))
    print("매도호가02 [%s]    잔량02 [%s]" % (recvvalue[4], recvvalue[24]))
    print("매도호가01 [%s]    잔량01 [%s]" % (recvvalue[3], recvvalue[23]))
    print("--------------------------------------")
    print("매수호가01 [%s]    잔량01 [%s]" % (recvvalue[13], recvvalue[33]))
    print("매수호가02 [%s]    잔량02 [%s]" % (recvvalue[14], recvvalue[34]))
    print("매수호가03 [%s]    잔량03 [%s]" % (recvvalue[15], recvvalue[35]))
    print("매수호가04 [%s]    잔량04 [%s]" % (recvvalue[16], recvvalue[36]))
    print("매수호가05 [%s]    잔량05 [%s]" % (recvvalue[17], recvvalue[37]))
    print("매수호가06 [%s]    잔량06 [%s]" % (recvvalue[18], recvvalue[38]))
    print("매수호가07 [%s]    잔량07 [%s]" % (recvvalue[19], recvvalue[39]))
    print("매수호가08 [%s]    잔량08 [%s]" % (recvvalue[20], recvvalue[40]))
    print("매수호가09 [%s]    잔량09 [%s]" % (recvvalue[21], recvvalue[41]))
    print("매수호가10 [%s]    잔량10 [%s]" % (recvvalue[22], recvvalue[42]))
    print("======================================")
    print("총매도호가 잔량        [%s]" % (recvvalue[43]))
    print("총매도호가 잔량 증감   [%s]" % (recvvalue[54]))
    print("총매수호가 잔량        [%s]" % (recvvalue[44]))
    print("총매수호가 잔량 증감   [%s]" % (recvvalue[55]))
    print("시간외 총매도호가 잔량 [%s]" % (recvvalue[45]))
    print("시간외 총매수호가 증감 [%s]" % (recvvalue[46]))
    print("시간외 총매도호가 잔량 [%s]" % (recvvalue[56]))
    print("시간외 총매수호가 증감 [%s]" % (recvvalue[57]))
    print("예상 체결가            [%s]" % (recvvalue[47]))
    print("예상 체결량            [%s]" % (recvvalue[48]))
    print("예상 거래량            [%s]" % (recvvalue[49]))
    print("예상체결 대비          [%s]" % (recvvalue[50]))
    print("부호                   [%s]" % (recvvalue[51]))
    print("예상체결 전일대비율    [%s]" % (recvvalue[52]))
    print("누적거래량             [%s]" % (recvvalue[53]))
    print("주식매매 구분코드      [%s]" % (recvvalue[58]))
"""


# 국내주식체결처리 출력라이브러리
def stockspurchase(data_cnt, data):
    print("============================================")
    menulist = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비부호|전일대비|전일대비율|가중평균주식가격|주식시가|주식최고가|주식최저가|매도호가1|매수호가1|체결거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분|매수비율|전일거래량대비등락율|시가시간|시가대비구분|시가대비|최고가시간|고가대비구분|고가대비|최저가시간|저가대비구분|저가대비|영업일자|신장운영구분코드|거래정지여부|매도호가잔량|매수호가잔량|총매도호가잔량|총매수호가잔량|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율|시간구분코드|임의종료구분코드|정적VI발동기준가"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
      ##  print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
       ##     print("%-13s[%s]" % (menu, pValue[i]))
            i += 1


# 국내주식체결통보 출력라이브러리
def stocksigningnotice_domestic(data, key, iv):
    
    # AES256 처리 단계
    aes_dec_str = aes_cbc_base64_dec(key, iv, data)
    pValue = aes_dec_str.split('^')

    if pValue[13] == '2': # 체결통보
##        print("#### 국내주식 체결 통보 ####")
        menulist = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|주문조건|주식단축종목코드|체결수량|체결단가|주식체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|호가조건가격|주문거래소구분|실시간체결창표시여부|필러|신용구분|신용대출일자|체결종목명40|주문가격"
        menustr1 = menulist.split('|')
    else:
##        print("#### 국내주식 주문·정정·취소·거부 접수 통보 ####")
        menulist = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|주문조건|주식단축종목코드|주문수량|주문가격|주식체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|호가조건가격|주문거래소구분|실시간체결창표시여부|필러|신용구분|신용대출일자|체결종목명40|체결단가"
        menustr1 = menulist.split('|')
    
    i = 0
    for menu in menustr1:
        print("%s  [%s]" % (menu, pValue[i]))
        i += 1


def data_processor_worker(worker_id, data_queue, stock_code):
    """
    데이터 처리 전용 워커 프로세스
    
    Args:
        worker_id: 워커 식별 번호
        data_queue: 메인 프로세스로부터 데이터를 받을 큐
        stock_code: 담당 종목코드
    """
    import sys
    
    process_id = os.getpid()
    print(f"\n{'#'*80}")
    print(f"[Processor-{worker_id}] 시작: PID={process_id}, 담당종목={stock_code}")
    print(f"{'#'*80}\n")
    
    processed_count = 0
    message = None  # 에러 추적용
    error_count = 0
    
    try:
        while True:
            try:
                # 큐에서 데이터 가져오기 (타임아웃 1초)
                message = data_queue.get(timeout=1.0)
                
                if message is None:  # 종료 신호
                    print(f"[Processor-{worker_id}] [PID:{process_id}] 종료 신호 수신")
                    break
                
                # 메시지 유효성 검사
                if not isinstance(message, dict):
                    print(f"[Processor-{worker_id}] [PID:{process_id}] 잘못된 메시지 타입: {type(message)}, 내용: {message}")
                    continue
                
                msg_type = message.get('type')
                data = message.get('data')
                source_stock = message.get('stock_code')
                
                if not msg_type:
                    print(f"[Processor-{worker_id}] [PID:{process_id}] 메시지 타입 없음: {message}")
                    continue
                
                if not source_stock:
                    print(f"[Processor-{worker_id}] [PID:{process_id}] 종목코드 없음: {message}")
                    continue
                
                # 자신이 담당하는 종목의 데이터만 처리
                if source_stock != stock_code:
                    continue
                
                processed_count += 1
                
                if msg_type == 'hoka':
                    print(f"[Processor-{worker_id}] [PID:{process_id}] [종목:{stock_code}] "
                          f"호가 데이터 처리 중... (처리건수: {processed_count})")
                    stockhoka(data)
                
                elif msg_type == 'chegyeol':
                    data_cnt = message.get('data_cnt', 1)
                    print(f"[Processor-{worker_id}] [PID:{process_id}] [종목:{stock_code}] "
                          f"체결 데이터 처리 중... (체결건수: {data_cnt}, 총처리: {processed_count})")
                    stockspurchase(data_cnt, data)
                
                elif msg_type == 'signing_notice':
                    aes_key = message.get('aes_key')
                    aes_iv = message.get('aes_iv')
                    print(f"[Processor-{worker_id}] [PID:{process_id}] [종목:{stock_code}] "
                          f"체결통보 처리 중... (처리건수: {processed_count})")
                    stocksigningnotice(data, aes_key, aes_iv)
                
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                
                # Queue.Empty는 정상 동작
                if "Empty" in str(type(e).__name__):
                    continue
                
                # 기타 에러는 상세 출력
                import traceback
                error_details = traceback.format_exc()
                
                print(f"\n{'!'*80}")
                print(f"[Processor-{worker_id}] [PID:{process_id}] 🔴 처리 에러 발생 (에러 #{error_count})")
                print(f"  에러 타입: {type(e).__name__}")
                print(f"  에러 메시지: '{error_msg}' (길이: {len(error_msg)})")
                print(f"  에러 repr: {repr(e)}")
                
                if message:
                    print(f"  문제 메시지 타입: {type(message)}")
                    try:
                        print(f"  문제 메시지 내용: {message}")
                    except:
                        print(f"  문제 메시지 내용: [출력 불가]")
                else:
                    print(f"  문제 메시지: None")
                
                print(f"\n  상세 스택 트레이스:")
                print(error_details)
                print(f"{'!'*80}\n")
                
                # 에러가 너무 많으면 종료
                if error_count > 100:
                    print(f"[Processor-{worker_id}] [PID:{process_id}] 에러 과다 발생으로 종료")
                    break
                
                continue
    
    except KeyboardInterrupt:
        print(f"[Processor-{worker_id}] [PID:{process_id}] 인터럽트로 종료")
    except Exception as e:
        print(f"[Processor-{worker_id}] [PID:{process_id}] 치명적 에러: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"[Processor-{worker_id}] [PID:{process_id}] 종료. 총 처리건수: {processed_count}, 에러: {error_count}")


def parse_stock_code_from_data(raw_data, trid):
    """
    실시간 데이터에서 종목코드 추출
    
    Args:
        raw_data: 파이프로 구분된 실시간 데이터
        trid: TR ID (H0STCNT0, H0STASP0 등)
    
    Returns:
        종목코드 (6자리)
    """
    try:
        # 디버깅: 처음 3번만 전체 데이터 출력
        if not hasattr(parse_stock_code_from_data, 'debug_count'):
            parse_stock_code_from_data.debug_count = 0
        
        if parse_stock_code_from_data.debug_count < 3:
            print(f"\n[DEBUG parse_stock_code] TR_ID: {trid}")
            print(f"[DEBUG parse_stock_code] Raw data: {raw_data[:200]}")
            parse_stock_code_from_data.debug_count += 1
        
        # 한국투자증권 실시간 데이터는 ^ 구분자로 필드가 나뉨
        fields = raw_data.split('^')
        
        if parse_stock_code_from_data.debug_count <= 3:
            print(f"[DEBUG parse_stock_code] 필드 개수: {len(fields)}")
            print(f"[DEBUG parse_stock_code] 첫 5개 필드: {fields[:5]}\n")
        
        if len(fields) > 0:
            # 첫 번째 필드가 보통 종목코드
            stock_code = fields[0].strip()
            
            # 종목코드 검증 (6자리 숫자)
            if stock_code.isdigit() and len(stock_code) == 6:
                return stock_code
        
        # 파싱 실패 시 None 반환
        return None
    except Exception as e:
        print(f"[parse_stock_code] 에러: {e}, data: {raw_data[:100]}")
        return None


async def websocket_receiver(url, approval_key, stock_codes, data_queues, custtype='P'):
    """
    단일 웹소켓 세션으로 여러 종목 데이터 수신
    수신한 데이터를 각 프로세스의 큐에 분배
    
    Args:
        url: 웹소켓 URL
        approval_key: 승인 키
        stock_codes: 구독할 종목 리스트
        data_queues: 각 워커의 데이터 큐 딕셔너리 {종목코드: Queue}
        custtype: 고객 타입
    """
    main_pid = os.getpid()
    aes_key = None
    aes_iv = None
    
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            print(f"\n{'='*80}")
            print(f"[WebSocket Main] PID: {main_pid}")
            print(f"[WebSocket Main] 연결 시도... URL: {url}")
            print(f"[WebSocket Main] 구독 종목: {', '.join(stock_codes)}")
            print(f"{'='*80}\n")
            
            async with websockets.connect(url, ping_interval=None) as websocket:
                # 웹소켓 세션 정보
                local_address = websocket.local_address
                remote_address = websocket.remote_address
                
                print(f"\n{'*'*80}")
                print(f"[WebSocket Main] 세션 정보")
                print(f"  - 메인 프로세스 PID: {main_pid}")
                print(f"  - 로컬 주소: {local_address[0]}:{local_address[1]}")
                print(f"  - 원격 주소: {remote_address[0]}:{remote_address[1]}")
                print(f"  - 웹소켓 객체 ID: {id(websocket)}")
                print(f"  - 구독 종목 수: {len(stock_codes)}")
                print(f"{'*'*80}\n")
                
                # 각 종목에 대해 구독 요청 전송
                for i, stock_code in enumerate(stock_codes):
                    await asyncio.sleep(0.5)  # 요청 간격
                    
                    senddata = {
                        "header": {
                            "approval_key": approval_key,
                            "custtype": custtype,
                            "tr_type": "1",
                            "content-type": "utf-8"
                        },
                        "body": {
                            "input": {
                                "tr_id": "H0STCNT0",  # 주식체결
                                "tr_key": stock_code
                            }
                        }
                    }
                    
                    senddata_str = json.dumps(senddata, ensure_ascii=False)
                    print(f"[WebSocket Main] [{i+1}/{len(stock_codes)}] 구독 요청: {stock_code}")
                    await websocket.send(senddata_str)
                
                retry_count = 0  # 연결 성공 시 재시도 카운트 초기화
                subscribe_count = 0
                
                # 데이터 수신 및 분배 루프
                print(f"\n[WebSocket Main] 데이터 수신 대기 중...\n")
                
                while True:
                    try:
                        data = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    except asyncio.TimeoutError:
                        print(f"[WebSocket Main] 타임아웃 - 연결 유지 중...")
                        continue
                    
                    # 실시간 데이터 처리 (0 또는 1로 시작)
                    if data[0] in ('0', '1'):
                        recvstr = data.split('|')
                        
                        if len(recvstr) < 4:
                            print(f"[WebSocket Main] Invalid data: {data}")
                            continue
                        
                        trid0 = recvstr[1]
                        raw_data = recvstr[3]
                        
                        # 실제 데이터에서 종목코드 추출
                        target_stock = parse_stock_code_from_data(raw_data, trid0)
                        
                        # 종목코드 추출 실패 또는 구독하지 않은 종목
                        if not target_stock:
                            print(f"[WebSocket Main] ⚠️  종목코드 추출 실패: {raw_data[:50]}...")
                            continue
                        
                        if target_stock not in data_queues:
                            print(f"[WebSocket Main] ⚠️  구독하지 않은 종목: {target_stock}")
                            continue
                        
                        if data[0] == '0':
                            # 주식호가
                            if trid0 == "H0STASP0":
                                message = {
                                    'type': 'hoka',
                                    'data': raw_data,
                                    'stock_code': target_stock
                                }
                                data_queues[target_stock].put(message)
                                print(f"[WebSocket Main] 호가 데이터 → Processor (종목: {target_stock})")
                            
                            # 주식체결
                            elif trid0 == "H0STCNT0":
                                data_cnt = int(recvstr[2])
                                message = {
                                    'type': 'chegyeol',
                                    'data': raw_data,
                                    'data_cnt': data_cnt,
                                    'stock_code': target_stock
                                }
                                data_queues[target_stock].put(message)
                                print(f"[WebSocket Main] 체결 데이터 → Processor (종목: {target_stock}, 건수: {data_cnt})")
                        
                        elif data[0] == '1':
                            # 주식체결 통보
                            if trid0 in ("K0STCNI0", "K0STCNI9", "H0STCNI0", "H0STCNI9"):
                                if aes_key and aes_iv:
                                    message = {
                                        'type': 'signing_notice',
                                        'data': raw_data,
                                        'aes_key': aes_key,
                                        'aes_iv': aes_iv,
                                        'stock_code': target_stock
                                    }
                                    data_queues[target_stock].put(message)
                                    print(f"[WebSocket Main] 체결통보 → Processor (종목: {target_stock})")
                    
                    # JSON 메시지 처리
                    else:
                        try:
                            jsonObject = json.loads(data)
                            trid = jsonObject["header"]["tr_id"]
                            
                            # PINGPONG 처리
                            if trid == "PINGPONG":
                                print(f"[WebSocket Main] RECV [PINGPONG]")
                                await websocket.send(data)
                                print(f"[WebSocket Main] SEND [PINGPONG]")
                            
                            # 일반 응답 처리
                            else:
                                rt_cd = jsonObject["body"]["rt_cd"]
                                tr_key = jsonObject["header"]["tr_key"]
                                msg = jsonObject["body"].get("msg1", "")
                                
                                if rt_cd == '1':  # 에러
                                    print(f"[WebSocket Main] ❌ ERROR [종목:{tr_key}] MSG [{msg}]")
                                
                                elif rt_cd == '0':  # 정상
                                    print(f"[WebSocket Main] ✓ SUCCESS [종목:{tr_key}] MSG [{msg}]")
                                    
                                    if "SUBSCRIBE SUCCESS" in msg or "SUCCESS" in msg:
                                        subscribe_count += 1
                                        print(f"[WebSocket Main] 🎉 구독 완료! ({subscribe_count}/{len(stock_codes)})")
                                    
                                    # AES 키 저장
                                    if trid in ("H0STCNI0", "H0STCNI9"):
                                        aes_key = jsonObject["body"]["output"]["key"]
                                        aes_iv = jsonObject["body"]["output"]["iv"]
                                        print(f"[WebSocket Main] AES KEY 저장: {aes_key[:20]}...")
                        
                        except json.JSONDecodeError as e:
                            print(f"[WebSocket Main] JSON error: {e}")
                        except KeyError as e:
                            print(f"[WebSocket Main] Key error: {e}")
        
        except websockets.exceptions.ConnectionClosed as e:
            print(f"[WebSocket Main] 연결 종료: {e}")
            retry_count += 1
            await asyncio.sleep(2 ** retry_count)
        
        except Exception as e:
            print(f"[WebSocket Main] Exception: {e}")
            import traceback
            traceback.print_exc()
            retry_count += 1
            await asyncio.sleep(2 ** retry_count)
    
    print(f"[WebSocket Main] 최대 재시도 횟수 초과")


def main():
    """메인 함수"""
    
    # API 키 설정
    g_appkey = '앱키 입력해주세요'
    g_appsecret = '앱시크릿키 입력해주세요'
    
    custtype = 'P'  # 개인
    url = 'ws://ops.koreainvestment.com:21000'  # 실전투자계좌
    # url = 'ws://ops.koreainvestment.com:31000'  # 모의투자계좌
    
    # 모니터링할 종목 리스트
    stock_codes = [
        '005930',  # 삼성전자
        '000660',  # SK하이닉스
        '035420',  # NAVER
        '005380',  # 현대차
        '051910',  # LG화학
    ]
    
    print(f"\n{'='*80}")
    print(f"메인 프로세스 PID: {os.getpid()}")
    print(f"구독 종목: {', '.join(stock_codes)}")
    print(f"{'='*80}\n")
    
    try:
        # 1. Approval key 발급
        print("=== Approval Key 발급 중 ===")
        approval_key = get_approval(g_appkey, g_appsecret)
        print(f"Approval Key: {approval_key}\n")
        
        # 2. 각 종목별 데이터 큐 생성 (Manager 사용)
        manager = Manager()
        data_queues = {}
        
        for stock_code in stock_codes:
            data_queues[stock_code] = manager.Queue(maxsize=1000)
        
        # 3. 데이터 처리 워커 프로세스 생성
        processes = []
        
        for i, stock_code in enumerate(stock_codes):
            worker_id = i + 1
            p = Process(
                target=data_processor_worker,
                args=(worker_id, data_queues[stock_code], stock_code)
            )
            p.start()
            processes.append(p)
            print(f"✓ Processor-{worker_id} 시작: PID={p.pid}, 종목={stock_code}")
            time.sleep(0.2)
        
        print(f"\n=== 모든 프로세서 시작 완료 ({len(processes)}개) ===\n")
        
        # 4. 웹소켓 수신 시작 (메인 프로세스에서 실행)
        print("=== 웹소켓 연결 시작 ===\n")
        asyncio.run(websocket_receiver(url, approval_key, stock_codes, data_queues, custtype))
    
    except KeyboardInterrupt:
        print("\n\n=== 프로그램 종료 중 ===")
        
        # 모든 워커에 종료 신호 전송
        for stock_code in stock_codes:
            try:
                data_queues[stock_code].put(None)
            except:
                pass
        
        # 프로세스 종료 대기
        for p in processes:
            p.join(timeout=2)
            if p.is_alive():
                p.terminate()
        
        print("모든 프로세서 종료 완료")
    
    except Exception as e:
        print(f"메인 프로세스 에러: {e}")
        import traceback
        traceback.print_exc()
        
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    main()