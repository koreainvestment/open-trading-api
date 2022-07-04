package com.ops;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class PrintOpsData {

	private static AES256 aes256;

	
	// 주식호가 처리
	public void stockhoka (String data)	{
		//System.out.printf("stockhoka[%s]", data);
		String[] recvvalue = data.split("\\^");
		
	    System.out.println("유가증권 단축 종목코드 [" + recvvalue[0] + "]");
	    System.out.println("영업시간 [" + recvvalue[1] + "]" + "시간구분코드 [" + recvvalue[2] + "]");
	    System.out.println("======================================");
	    System.out.printf("매도호가09 [%s]    잔량09 [%s]\r\n", recvvalue[11], recvvalue[31]);
	    System.out.printf("매도호가08 [%s]    잔량08 [%s]\r\n", recvvalue[10], recvvalue[30]);
	    System.out.printf("매도호가07 [%s]    잔량07 [%s]\r\n", recvvalue[9], recvvalue[29]);
	    System.out.printf("매도호가06 [%s]    잔량06 [%s]\r\n", recvvalue[8], recvvalue[28]);
	    System.out.printf("매도호가05 [%s]    잔량05 [%s]\r\n", recvvalue[7], recvvalue[27]);
	    System.out.printf("매도호가04 [%s]    잔량04 [%s]\r\n", recvvalue[6], recvvalue[26]);
	    System.out.printf("매도호가03 [%s]    잔량03 [%s]\r\n", recvvalue[5], recvvalue[25]);
	    System.out.printf("매도호가02 [%s]    잔량02 [%s]\r\n", recvvalue[4], recvvalue[24]);
	    System.out.printf("매도호가01 [%s]    잔량01 [%s]\r\n", recvvalue[3], recvvalue[23]);
	    System.out.println("--------------------------------------");
	    System.out.printf("매수호가01 [%s]    잔량01 [%s]\r\n", recvvalue[13], recvvalue[33]);
	    System.out.printf("매수호가02 [%s]    잔량02 [%s]\r\n", recvvalue[14], recvvalue[34]);
	    System.out.printf("매수호가03 [%s]    잔량03 [%s]\r\n", recvvalue[15], recvvalue[35]);
	    System.out.printf("매수호가04 [%s]    잔량04 [%s]\r\n", recvvalue[16], recvvalue[36]);
	    System.out.printf("매수호가05 [%s]    잔량05 [%s]\r\n", recvvalue[17], recvvalue[37]);
	    System.out.printf("매수호가06 [%s]    잔량06 [%s]\r\n", recvvalue[18], recvvalue[38]);
	    System.out.printf("매수호가07 [%s]    잔량07 [%s]\r\n", recvvalue[19], recvvalue[39]);
	    System.out.printf("매수호가08 [%s]    잔량08 [%s]\r\n", recvvalue[20], recvvalue[40]);
	    System.out.printf("매수호가09 [%s]    잔량09 [%s]\r\n", recvvalue[21], recvvalue[41]);
	    System.out.printf("매수호가10 [%s]    잔량10 [%s]\r\n", recvvalue[22], recvvalue[42]);
	    System.out.println("======================================");
	    System.out.printf("총매도호가 잔량        [%s]\r\n",recvvalue[43]);
	    System.out.printf("총매도호가 잔량 증감    [%s]\r\n",recvvalue[54]);
	    System.out.printf("총매수호가 잔량        [%s]\r\n",recvvalue[44]);
	    System.out.printf("총매수호가 잔량 증감    [%s]\r\n",recvvalue[55]);
	    System.out.printf("시간외 총매도호가 잔량  [%s]\r\n",recvvalue[45]);
	    System.out.printf("시간외 총매수호가 증감  [%s]\r\n",recvvalue[46]);
	    System.out.printf("시간외 총매도호가 잔량  [%s]\r\n",recvvalue[56]);
	    System.out.printf("시간외 총매수호가 증감  [%s]\r\n",recvvalue[57]);
	    System.out.printf("예상 체결가           [%s]\r\n",recvvalue[47]);
	    System.out.printf("예상 체결량           [%s]\r\n",recvvalue[48]);
	    System.out.printf("예상 거래량           [%s]\r\n",recvvalue[49]);
	    System.out.printf("예상체결 대비          [%s]\r\n",recvvalue[50]);
	    System.out.printf("부호                 [%s]\r\n",recvvalue[51]);
	    System.out.printf("예상체결 전일대비율     [%s]\r\n",recvvalue[52]);
	    System.out.printf("누적거래량            [%s]\r\n",recvvalue[53]);
	    System.out.printf("주식매매 구분코드       [%s]\r\n",recvvalue[58]);
		
	}
	
	// 주식체결통보 처리
	public void stocksigningnotice (String data)	{
		aes256 = new AES256();
	
		String menulistJ = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|주문조건|주식단축종목코드|체결수량|체결단가|주식체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|체결종목명|신용구분|신용대출일자|체결종목명40|주문가격";
		String[] arrMenu = menulistJ.split("\\|");
		
		try	{
			String pData = null;
			pData = aes256.decrypt(data, WebSocketOps.Key, WebSocketOps.iv);
			String[] arrValue = pData.split("\\^");
			
			System.out.println("=======================================================");
			for (int i=0; i<arrValue.length;i++)	{
				System.out.printf("%-12s : [%s]\r\n", arrMenu[i], arrValue[i]);
			}
			System.out.println("=======================================================");
		} catch (Exception e)	{
			System.out.println(e);
		}
	}
	
	// 주식체결 처리
	public void stockspurchase(String data)	{
		String menulistJ = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비부호|전일대비|전일대비율|가중평균주식가격|주식시가|주식최고가|주식최저가|매도호가1|매수호가1|체결거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분|매수비율|전일거래량대비등락율|시가시간|시가대비구분|시가대비|최고가시간|고가대비구분|고가대비|최저가시간|저가대비구분|저가대비|영업일자|신장운영구분코드|거래정지여부|매도호가잔량|매수호가잔량|총매도호가잔량|총매수호가잔량|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율|시간구분코드|임의종료구분코드|정적VI발동기준가";
		String[] arrMenu = menulistJ.split("\\|");
		String[] arrValue = data.split("\\^");
		
		System.out.println("=======================================================");
		for (int i=0; i<arrMenu.length;i++)	{
			System.out.printf("%-12s : [%s]\r\n", arrMenu[i], arrValue[i]);
		}
		System.out.println("=======================================================");
	}
	
	void printMessage(String message) {
		
		System.out.println("[RECV] :"+message.toString());
		
		char fStr = message.charAt(0);
		
		// 첫데이터로 전문인지 json 데이터인지 구분을해서 처리를 해야한다.
		if(fStr == '0') {
			// 암호화 되지 않은 전문 처리
				String[] mData = message.split("\\|");
				String tr_id = mData[1];
				//System.out.println("trid : "+tr_id);
				
				switch (tr_id)	{
					case "H0STASP0":
						System.out.println("["+tr_id+"]"+"###################################################");
						stockhoka(mData[3]);
						break;
					case "H0STCNT0":
						System.out.println("["+tr_id+"]"+"###################################################");
						stockspurchase(mData[3]);
						break;
					default:
						break;
				}
		
		}else if(fStr == '1') {
			// 암호화 된 전문 처리, 주식체결통보 데이터만 암호화 되서 오므로 해당데이터만 처리
			String[] mData = message.split("\\|");
			String tr_id = mData[1];
			//System.out.println("trid : "+tr_id);
			
			switch (tr_id)	{
				case "H0STCNI0":	// 주식체결통보(고객용)
				case "H0STCNI9":	// 주식체결통보(모의투자)
					System.out.println("["+tr_id+"]"+"###################################################");
					stocksigningnotice(mData[3]);
					break;
				default:
					break;
			}
			
		}else {
			// 일반 json 처리
			JSONParser parser = new JSONParser();
			Object obj;
			JSONObject jsonObj;
			try {
				obj = parser.parse(message);
				jsonObj = (JSONObject) obj;
				//System.out.println("================================");
				
				//System.out.println("[RECV] :"+jsonObj.toString());
				JSONObject header = (JSONObject) jsonObj.get("header");
								
				String tmp_key = "";
				String tmp_iv = "";
				
				// tr_id 로 데이터처리를 구분한다.
				String tr_id = header.get("tr_id").toString();
				
				// 일반 요청에 대한 응답 데이터일 경우
				if (!(tr_id.equals("PINGPONG")))
				{
					// 일반 요청에 대한 응답 데이터에만 body 가 있다.
					JSONObject body = (JSONObject) jsonObj.get("body");
					String rt_cd = body.get("rt_cd").toString();
					
					String rt_msg = body.get("msg_cd").toString();
					String msg = body.get("msg1").toString();
					// rt_cd 가 '0'인경우에만 처리한다.
					if (rt_cd.equals("0"))	{
						JSONObject output = (JSONObject) body.get("output");
						//String rt_msg = body.get("msg_cd").toString();
						tmp_key = output.get("key").toString();
						tmp_iv = output.get("iv").toString();				
					} else {
						rt_msg = body.get("msg1").toString();
					}
				
			
					switch (tr_id)	{
						case "H0STASP0":	// 주식호가
							System.out.println("주식호가 ["+rt_msg+"] ["+msg+"]");
							break;
						case "H0STCNT0":
							System.out.println("주식체결 ["+rt_msg+"] ["+msg+"]");
							break;
						case "H0STCNI0":	// 주식체결통보(고객용)
						case "H0STCNI9":	// 주식체결통보(모의투자)
							System.out.println("주식체결통보 ["+rt_msg+"] ["+msg+"]");
							// 체결통보일 경우 복호화를 해야 하므로 key, iv를 저장해서 쓴다.
							WebSocketOps.Key = tmp_key;
							WebSocketOps.iv = tmp_iv;
							System.out.printf(">> [%s] : SAVE KEY[%s] IV[%s]\r\n", tr_id, tmp_key, tmp_iv);
							//stocksigningnotice(message);
							break;
						default:					
							break;
					}
				}
				else if (tr_id.equals("PINGPONG"))	// PINGPONG 데이터일 경우
				{
					WebSocketOps.clientEndPoint.sendMessage(message);
					System.out.println("[SEND] :"+ message);
				}
				
			} catch (ParseException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
		}	
		
	}
}
