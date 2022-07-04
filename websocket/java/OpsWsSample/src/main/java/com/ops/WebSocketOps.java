package com.ops;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Map;
import java.util.Properties;
import java.util.HashMap;
import java.util.Scanner;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;


public class WebSocketOps {
	
	// properties 파일 처리
	public Properties readProperties(String propFileName) {
	    Properties prop = new Properties();
	    InputStream inputStream = getClass().getClassLoader().getResourceAsStream(propFileName);
	    
	    try {
	        if (inputStream != null) {
	            prop.load(inputStream);
	            return prop;
	        } else {
	            throw new FileNotFoundException("프로퍼티 파일 '" + propFileName + "'을 resource에서 찾을 수 없습니다.");
	        }
	    } catch (IOException e) {
	        e.printStackTrace();
	        return null;
	    }
	}
	
	private static String sMessage = "static message";
	
	static WebsocketClientEndpoint clientEndPoint = null;
	
	private static boolean bContinue = true;
	// json environment
	/*
	 * String appkey =
	 * "SeP0yXDOgguXRY4sl305ViBLSRmnNpHi99iWqrFbXPqL+LgBRshYstu/w7Iknn/k"; String
	 * appsceret =
	 * "s8w9coyUrF/4NjCrj2LKI5jPCqpXRbyC4LlayKaDxRLILyZDd8e81BDxQOtTlWq4F23HFN838PZ2IHxbv2CkAA0mZ6JZDiAplWGGG/JAdx5VtbiXFe3GDPL/2rWraUXvmWpXlqsgLgoQR1D9nxirn4DihMdJJKMo2Kp55/cqncfkJEt5ECk=";
	 * String personalsecKey =
	 * "s8w9coyUrF/4NjCrj2LKI5jPCqpXRbyC4LlayKaDxRLILyZDd8e81BDxQOtTlWq4F23HFN838PZ2IHxbv2CkAA0mZ6JZDiAplWGGG/JAdx5VtbiXFe3GDPL/2rWraUXvmWpXlqsgLgoQR1D9nxirn4DihMdJJKMo2Kp55/cqncfkJEt5ECk=";
	 * String custType = "P"; String contentType = "utf-8"; // content type String
	 * stockCode = "005930"; // stock code String htsId = "101334"; // hts id
	 */    
    
    // aes256 key, iv
    static String Key = null;	// 32byte
    static String iv = null;	// 16byte
    
    static String appkey = null;
    static String appsecret = null;
    static String personalsecKey = null;
    static String custType = null;
    static String contentType = null;
    static String stockCode = null;
    static String htsId = null;
    
	private void showMessage() {
		System.out.println("[MENU] =============================================================================================================================================");
        System.out.println("1.주식호가, 2.주식호가해제, 3.주식체결, 4.주식체결해제, 7.주식체결통보(모의), 8.주식체결통보해제(모의), 0.종료");
        System.out.println("====================================================================================================================================================");
        
        // Insert Input Value
        System.out.printf("InputValue : ");
        Scanner sc = new Scanner(System.in);
        String inputValue = sc.nextLine();
        
        String trId = null;
        String trType = null;
        String signingNotice = "N";	// 체결통보 flag
        
        switch (inputValue) {
        	case "1":	// 주식호가 등록
        		trId = "H0STASP0";
        		trType = "1";
        		break;
        	case "2":	// 주식호가 등록취소
        		trId = "H0STASP0";
        		trType = "2";
        		break;
        	case "3":  // 주식체결 등록
        		trId = "H0STCNT0";
        		trType = "1";
        		break;
        	case "4":  // 주식체결 등록해제
        		trId = "H0STCNT0";
        		trType = "2";
        		break;
        	case "7":  // 주식체결통보 등록(모의)
        		trId = "H0STCNI9";  // 테스트용 모의체결통보
        		trType = "1";
        		signingNotice = "Y";
        		break;
        	case "8":  // 주식체결통보 등록해제(모의)
        		trId = "H0STCNI9";  // 테스트용 직원체결통보
        		trType = "2";
        		signingNotice = "Y";
                break;
        	case "0":
        		System.out.println("Ops Connection End!!");
        		bContinue = false;
        		break;
        	default:
        		System.out.println("Wrong Input Value!! ["+inputValue+"]");
        		bContinue = false;
        		break;
        }

        //'{"header":{"authoriztion":"","appkey":"' + g_appkey + '","appsecret":"' + g_appseceret + '","personalseckey":"' + g_personalsecKey + '","custtype":"P","tr_type":"' + tr_type + '","content-type":"utf-8"},"body":{"input":{"tr_id":"' + tr_id + '","tr_key":"' + stockcode + '"}}}'
       
        // json header
        Map<String,Object> sendhjs = new HashMap<String,Object>();
        sendhjs.put("appkey", appkey);
        sendhjs.put("appsecret", appsecret);
        sendhjs.put("personalseckey", personalsecKey);
        sendhjs.put("custtype", custType);
        sendhjs.put("tr_type", trType);
        sendhjs.put("content-type", contentType);
        
        // json body 
        Map<String, Object> sendbjs = new HashMap<String, Object>();
        sendbjs.put("tr_id", trId);
        
        // 체결통보는 trkey값을 htsid를 넣어 처리한다.
        if (signingNotice.equals("Y"))	{
        	sendbjs.put("tr_key", htsId);
        } else {
        	sendbjs.put("tr_key", stockCode);
        }
        signingNotice = null;	// 체결통보 초기화처리
        
        Map<String, Object> data = new HashMap<String, Object>();
        data.put("header", sendhjs);
        
        Map<String, Object> data2 = new HashMap<String, Object>();
        data2.put("input", sendbjs);
        
        data.put("body", data2);
        
        try	{
	        String sendJson = null;
	        sendJson = new ObjectMapper().writeValueAsString(data);
	        
	        
	        if (bContinue == true)	{
	        	System.out.println("[SEND] :"+sendJson);
	        	clientEndPoint.sendMessage(sendJson);
	        }
	        
	        Thread.sleep(1000);
	        
        } catch (JsonProcessingException e1 )	{
        	
        	System.out.println(e1.getMessage());
        	
        }catch(InterruptedException e2) {
        	System.out.println(e2.getMessage());
        }finally {
			//System.out.println("종료 됨");
		}
        
        
	}
	
	public static void main (String[] args)	{
        try	{
        	WebSocketOps ops = new WebSocketOps();
       
        	Properties prop = ops.readProperties("ops.properties");
            
        	// ops.properties 의 값을 가져온다.
        	String uri = prop.getProperty("url");
        	String pport = prop.getProperty("port");
        	appkey = prop.getProperty("appkey");
        	appsecret = prop.getProperty("appsecret");
        	personalsecKey = prop.getProperty("personalsecKey");
        	custType = prop.getProperty("custType");
        	contentType = prop.getProperty("contentType");
        	stockCode = prop.getProperty("stockCode");
        	htsId = prop.getProperty("htsId");
        	
        	System.out.println("## 읽은정보 출력 ##############");
        	System.out.println("연결 uri : "+uri);
        	System.out.println("연결 port : "+pport);
        	System.out.println("############################");

      	
			// open websocket
	        clientEndPoint = new WebsocketClientEndpoint(new URI(uri+":"+pport));
	        
	        
	        // add listener
	        clientEndPoint.addMessageHandler(new WebsocketClientEndpoint.MessageHandler() {
	            public void handleMessage(String message) {
	                System.out.println(message);
	            }
	        });
	        
	        // loop menu
	        while(bContinue) {
	        	ops.showMessage();	        	
	        }
	        
	    } catch (URISyntaxException ex) {
	        System.err.println("URISyntaxException exception: " + ex.getMessage());
	    }
	}
}
