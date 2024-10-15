using System.Data;
using KIS_Common;
using KIS_Domestic;
using KIS_Oversea;


public class Program {

    public static void Main(String [] args) {
        
        Program p = new Program();
        p.CallForeignStock();

    }

    public async void CallForeignStock() {

        // 파이썬에서 Dataframe 으로 처리하던 방식을 DataTable, DataRow 사용방식으로 변경
        DataTable rt_data  = new DataTable(); 

        // [공통] 토큰 발급 및 갱신 처리
        // 별도 경로 지정한 yaml 파일 값을 읽어와서 처리
        // 사용 인수 : P (실전투자) 또는 V (모의투자)
        await Common.doAuth("D");

        // [해외주식] 주문/계좌 ===================================================================================================================================
        // [해외주식] 주문/계좌 > 주문 (매수매도구분 buy,sell + 종목코드6자리 + 주문수량 + 주문단가)
        // 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 KIS_OvrseaStk.cs GetOverseasOrder 수정요망!
        // rt_data = KIS_OverseaStk.get_overseas_order(ord_dv="buy", excg_cd="NASD", itm_no="TSLA", qty=1, unpr=170)
        // rt_data = KIS_OverseaStk.get_overseas_order(ord_dv="buy", excg_cd="NASD", itm_no="AAPL", qty=1, unpr=216.75)
        rt_data = KIS_OverseaStk.GetOverseasOrder ("buy", "AMEX", "SGOV", "00", 1, 4335);
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data); // # 주문접수조직번호+주문접수번호+주문시각

        // [해외주식] 주문/계좌 > 정정취소주문 (해외거래소코드excg_cd + 종목코드itm_no + 주문번호orgn_odno + 정정취소구분rvse_cncl_dvsn_cd + 수량qty + 주문단가unpr)
        // 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 KIS_OvrseaStk.cs GetOverseasOrder 수정요망!
        rt_data = KIS_OverseaStk.GetOverseasOrderRvseCncl("NASD", "TSLA", "0030089601", "02", 1, 0);
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data); // # 주문접수조직번호+주문접수번호+주문시각

        // [해외주식] 주문/계좌 > 해외주식 미체결내역 (해외거래소코드)
        // 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        rt_data = KIS_OverseaStk.GetOverseasInquireNccs("NYSE");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외주식 미체결전량취소주문 (해외거래소코드excg_cd + 종목코드itm_no)
        // 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        rt_data = KIS_OverseaStk.GetOverseasOrderAllCncl("NASD", "");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외주식 잔고 현황
        // 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        // 거래통화코드 - USD : 미국달러,HKD : 홍콩달러,CNY : 중국위안화,JPY : 일본엔화,VND : 베트남동
        rt_data = KIS_OverseaStk.GetOverseasInquireBalance("NASD", "");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외주식 잔고 내역
        // 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        // 거래통화코드 - USD : 미국달러,HKD : 홍콩달러,CNY : 중국위안화,JPY : 일본엔화,VND : 베트남동
        rt_data = KIS_OverseaStk.GetOverseasInquireBalanceLst("NASD", "");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외주식 주문체결내역
        // 해외거래소코드 NASD:미국시장 전체(나스닥,뉴욕,아멕스),NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
        rt_data = KIS_OverseaStk.GetOverseasInquireCcnl("", "", "");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외주식 체결기준현재잔고
        // dv : 01 보유종목, 02 외화잔고, 03 체결기준현재잔고
        // dvsn : 01 원화, 02 외화
        // natn 국가코드 : 000 전체,840 미국,344 홍콩,156 중국,392 일본,704 베트남
        // mkt 거래시장코드 [Request body NATN_CD 000 설정]
        // 00 : 전체 , (NATN_CD 840 인경우) 00:전체,01:나스닥(NASD),02:뉴욕거래소(NYSE),03:미국(PINK SHEETS),04:미국(OTCBB),05:아멕스(AMEX) (다른시장 API문서 참조)
        rt_data = KIS_OverseaStk.GetOverseasInquirePresentBalance("02", "01", "000", "00", "00");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 미국주간주문 (매수매도구분 buy,sell + 종목번호 + 주문수량 + 주문단가)
        // 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 KIS_OvrseaStk.cs GetOverseasOrder 수정요망
        // !! 현재 미국주간주문은 일시적으로 중단되어 있으며, 추후 재개는 한국투자증권 홈페이지를 통해 공지 예정입니다.
        // rt_data = KIS_OverseaStk.GetOverseasDaytimeOrder("buy", "NASD", "TSLA", 1, 251);
        // rt_data = KIS_OverseaStk.GetOverseasDaytimeOrder("buy", "NASD", "AAPL", 1, 216.75);
        rt_data = KIS_OverseaStk.GetOverseasDaytimeOrder("buy", "NASD", "NVDA", 1, 123.3);
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 미국주간정정취소 (해외거래소코드excg_cd + 종목코드itm_no + 주문번호orgn_odno + 정정취소구분rvse_cncl_dvsn_cd + 수량qty + 주문단가unpr)
        // 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 KIS_OvrseaStk.cs GetOverseasOrder 수정요망!
        // !! 현재 미국주간주문은 일시적으로 중단되어 있으며, 추후 재개는 한국투자증권 홈페이지를 통해 공지 예정입니다.
        rt_data = KIS_OverseaStk.GetOverseasDaytimeOrderRvseCncl("NASD", "TSLA", "0030089601", "02", 1, 0);
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data); // 주문접수조직번호+주문접수번호+주문시각

        // [해외주식] 주문/계좌 > 해외주식 기간손익[v1_해외주식-032] (해외거래소코드 + 통화코드 + 종목번호 6자리 + 조회시작일 + 조회종료일)
        // 해외거래소코드 - 미입력 : 전체, NASD:미국, SEHK:홍콩, SHAA:중국 상해, TKSE:일본, HASE:베트남
        rt_data = KIS_OverseaStk.GetOverseasInquirePeriodProfit("", "", "", "20240601", "20240709");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외주식 기간손익(매매일자종목별 기간손익) (해외거래소코드 + 통화코드 + 종목번호 6자리 + 조회시작일 + 조회종료일)
        rt_data = KIS_OverseaStk.GetOverseasInquirePeriodProfitOutput1("NASD", "" , "", "20240501", "20240709");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외증거금 통화별조회
        rt_data = KIS_OverseaStk.GetOverseasInquireForeignMargin();
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외증거금 일별거래내역 (해외거래소코드 + 매도매수구분코드 + 종목번호 6자리 + 조회시작일 + 조회종료일)
        rt_data = KIS_OverseaStk.GetOverseasInquirePeriodTrans("", "", "",  "20240601", "20240709");
        // [해외주식] 주문/계좌 > 해외증거금 일별거래내역[합계]
        rt_data = KIS_OverseaStk.GetOverseasInquirePeriodTransOutput2("", "", "",  "20240601", "20240709");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 주문/계좌 > 해외주식 결제기준현재잔고
        // dv : 01 보유종목, 02 외화잔고, 03 결제기준현재잔고
        // dt : 기준일자(YYYYMMDD)
        // dvsn : 01 원화, 02 외화
        // inqr_dvsn : 00(전체), 01(일반), 02(미니스탁)
        rt_data = KIS_OverseaStk.GetOverseasInquirePaymtStdrBalance("03", "", "01", "00");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세  ===================================================================================================================================
        // [해외주식] 기본시세 > 해외주식 현재체결가 (해외거래소코드, 종목번호)
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotPrice ("NAS", "AAPL");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세 > 해외주식 기간별시세
        // ※ 기준일(bymd) 지정일자 이후 100일치 조회, 미입력시 당일자 기본 셋팅
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotDailyPrice("NAS", "AAPL", "0", "");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세 > 해외주식 종목/지수/환율기간별시세(일/주/월/년)
        // ※ 기준일(bymd) 지정일자 이후 100일치 조회, 미입력시 당일자 기본 셋팅
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotInquireDailyPrice("N", "AAPL" , "", "", "D");
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotInquireDailyChartPrice ("N", "AAPL" , "20240605", "20240610", "D");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세 > 해외주식조건검색  div 01 : 검색결과종목수, 02:검색결과종목리스트
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotInquireSearch ("02", "NAS", "160", "170");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세 > 해외결제일자조회 (기준일자)
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotCountriesHoliday("");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세 > 해외주식 현재가상세 (해외거래소시장코드, 종목코드)
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotPriceDetail("NAS", "AAPL");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);  

        // [해외주식] 기본시세 > 해외주식 해외주식분봉조회 (조회구분 div-02:분봉데이터,01:시장별장운영시간, 해외거래소시장코드, 종목코드, 분갭, 전일포함여부)
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotInquireTimeItemChartPrice("02", "NAS", "AAPL" , "", "0");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세 > 해외주식 해외지수분봉조회 (조회구분 div-02:분봉데이터,01:지수정보, 조건시장분류코드, 입력종목코드, 시간구분코드, 과거데이터포함여부)
        rt_data = KIS_OverseaStk.GetOverseasPriceQuotInquireTimeIndexChartPrice("02", "N", "SPX", "0", "Y");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세 > 해외주식 상품기본정보 (종목번호, 종목유형)
        // 종목유형 : 512 미국 나스닥/513 미국 뉴욕/529 미국 아멕스/515 일본/501 홍콩/543 홍콩CNY/558 홍콩USD/507 베트남 하노이/508 베트남 호치민/551 중국 상해A/552 중국 심천A
        rt_data = KIS_OverseaStk.GetOverseasPriceSearchInfo ("AAPL", "512");
        //print("종목코드("+rt_data.std_pdno+") 종목명(" +rt_data.prdt_eng_name+") 거래시장(" +rt_data.ovrs_excg_cd+":" +rt_data.tr_mket_name+")") 
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);

        // [해외주식] 기본시세 > 해외주식 현재가 10호가 (조회구분 01:기본시세 02:10호가 , 해외거래소코드, 종목번호)
        rt_data = KIS_OverseaStk.GetOverseasPriceInquireAskingPrice("02", "NAS", "AAPL");
        if (rt_data is not null && rt_data.Rows.Count > 0 ) Common.PrintDataTable(rt_data);



    }

}
