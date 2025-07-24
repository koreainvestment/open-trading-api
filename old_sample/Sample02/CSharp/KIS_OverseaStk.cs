using System.Data;
using Newtonsoft.Json.Linq;
using KIS_Common;
using Newtonsoft.Json;

namespace KIS_Oversea
{
    class KIS_OverseaStk
    {
        /*
        #====|  [해외주식] 주문/계좌  |============================================================================================================================

        ##############################################################################################
        # [해외주식] 주문/계좌 > 해외주식 주문[v1_해외주식-001]
        #
        # * 모의투자의 경우, 모든 해외 종목 매매가 지원되지 않습니다. 일부 종목만 매매 가능한 점 유의 부탁드립니다.
        #
        # * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        # https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
        #
        # * 해외 거래소 운영시간 외 API 호출 시 애러가 발생하오니 운영시간을 확인해주세요.
        # * 해외 거래소 운영시간(한국시간 기준)
        # 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        # 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        # 3) 상해 : 10:30 ~ 16:00
        # 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00
        #
        # ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
        # (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
        #
        # ※ 종목코드 마스터파일 정제코드는 한국투자증권 Github 파이썬 참고 부탁드립니다.
        # https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
        ##############################################################################################
        # Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
        # Output: dataTable (Option) output API 문서 참조 등
        */     
        // ord_dv="", excg_cd="", itm_no="", qty=0, unpr=0, trCont="", FK100="", NK100="", dataTable=None  
        public static DataTable GetOverseasOrder(string ord_dv="", string excg_cd="", string itm_no="", string ord_dvsn = "00", double qty=0, double unpr=0, string trCont="", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/order";
            string trID;

            if (ord_dv == "buy")
            {
                switch (excg_cd)
                {
                    case "NASD":
                    case "NYSE":
                    case "AMEX":
                        trID = "TTTT1002U"; // 미국 매수 주문 [모의투자] VTTT1002U
                        break;
                    case "SHEK":
                        trID = "TTTS1002U"; // 홍콩 매수 주문 [모의투자] VTTS1002U
                        break;
                    case "SHAA":
                        trID = "TTTS0202U"; // 중국상해 매수 주문 [모의투자] VTTS0202U
                        break;
                    case "SZAA":
                        trID = "TTTS0305U"; // 중국심천 매수 주문 [모의투자] VTTS0305U
                        break;
                    case "TKSE":
                        trID = "TTTS0308U"; // 일본 매수 주문 [모의투자] VTTS0308U
                        break;
                    case "HASE":
                    case "VNSE":
                        trID = "TTTS0311U"; // 베트남(하노이,호치민) 매수 주문 [모의투자] VTTS0311U
                        break;
                    default:
                        Console.WriteLine("해외거래소코드 확인요망!!!");
                        return null;
                }
            }
            else if (ord_dv == "sell")
            {
                switch (excg_cd)
                {
                    case "NASD":
                    case "NYSE":
                    case "AMEX":
                        trID = "TTTT1006U"; // 미국 매도 주문 [모의투자] VTTT1006U
                        break;
                    case "SHEK":
                        trID = "TTTS1001U"; // 홍콩 매도 주문 [모의투자] VTTS1001U
                        break;
                    case "SHAA":
                        trID = "TTTS1005U"; // 중국상해 매도 주문 [모의투자] VTTS1005U
                        break;
                    case "SZAA":
                        trID = "TTTS0304U"; // 중국심천 매도 주문 [모의투자] VTTS0304U
                        break;
                    case "TKSE":
                        trID = "TTTS0307U"; // 일본 매도 주문 [모의투자] VTTS0307U
                        break;
                    case "HASE":
                    case "VNSE":
                        trID = "TTTS0310U"; // 베트남(하노이,호치민) 매도 주문 [모의투자] VTTS0311U
                        break;
                    default:
                        Console.WriteLine("해외거래소코드 확인요망!!!");
                        return null;
                }
            }
            else
            {
                Console.WriteLine("매수/매도 구분 확인요망!");
                return null;
            }

            if (string.IsNullOrEmpty(itm_no))
            {
                Console.WriteLine("주문종목번호(상품번호) 확인요망!!!");
                return null;
            }

            if (qty == 0)
            {
                Console.WriteLine("주문수량 확인요망!!!");
                return null;
            }

            if (unpr == 0)
            {
                Console.WriteLine("해외주문단가 확인요망!!!");
                return null;
            }

            string sll_type = ord_dv == "buy" ? "" : "00";

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct }, // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod },  // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd },                    // 해외거래소코드
                { "PDNO", itm_no },                             // 종목코드
                { "ORD_DVSN", ord_dvsn },                       // 주문구분 00:지정가, 01:시장가, 02:조건부지정가  나머지주문구분 API 문서 참조
                { "ORD_QTY", qty.ToString() },                  // 주문주식수
                { "OVRS_ORD_UNPR", unpr.ToString() },           // 해외주문단가
                { "CTAC_TLNO", "" },
                { "MGCO_APTM_ODNO", "" },
                { "SLL_TYPE", sll_type },                       // 판매유형
                { "ORD_SVR_DVSN_CD", "0" }                      // 주문서버구분코드
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont);

            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;

        }
 
        public static DataTable GetOverseasOrderRvseCncl(string excg_cd = "", string itm_no = "", string? orgn_odno = "", string rvse_cncl_dvsn_cd = "", double qty = 0, double unpr = 0, string trCont = "")
        {

            string url = "/uapi/overseas-stock/v1/trading/order-rvsecncl";
            string trID;
            DataTable dataTable = new DataTable();

            switch (excg_cd)
            {
                case "NASD":
                case "NYSE":
                case "AMEX":
                    trID = "TTTT1004U"; // 미국 매수 주문 [모의투자] VTTT1004U
                    break;
                case "SHEK":
                    trID = "TTTS1003U"; // 홍콩 매수 주문 [모의투자] VTTS1003U
                    break;
                case "SHAA":
                    trID = "TTTS0302U"; // 중국상해 매수 주문 [모의투자] VTTS0302U
                    break;
                case "SZAA":
                    trID = "TTTS0306U"; // 중국심천 매수 주문 [모의투자] VTTS0306U
                    break;
                case "TKSE":
                    trID = "TTTS0309U"; // 일본 매수 주문 [모의투자] VTTS0309U
                    break;
                case "HASE":
                case "VNSE":
                    trID = "TTTS0312U"; // 베트남(하노이,호치민) 매수 주문 [모의투자] VTTS0312U
                    break;
                default:
                    Console.WriteLine("해외거래소코드 확인요망!!!");
                    return null;
            }

            if (string.IsNullOrEmpty(orgn_odno))
            {
                Console.WriteLine("원주문번호 확인요망!!!");
                return null;
            }

            if (!new[] { "01", "02" }.Contains(rvse_cncl_dvsn_cd))
            {
                Console.WriteLine("정정취소구분코드 확인요망!!!"); // 정정:01. 취소:02
                return null;
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },     // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd },            // 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
                { "PDNO", itm_no },                     // 종목번호(상품번호)
                { "ORGN_ODNO", orgn_odno },             // 원주문번호 정정 또는 취소할 원주문번호 (해외주식_주문 API ouput ODNO or 해외주식 미체결내역 API output ODNO 참고)
                { "RVSE_CNCL_DVSN_CD", rvse_cncl_dvsn_cd }, // 정정 : 01, 취소 : 02
                { "ORD_QTY", qty.ToString() },           // 주문수량	[잔량전부 취소/정정주문] "0" 설정 ( QTY_ALL_ORD_YN=Y 설정 ) [잔량일부 취소/정정주문] 취소/정정 수량
                { "OVRS_ORD_UNPR", unpr.ToString() },    // 주문단가 	[정정] 정정주문 1주당 가격 [취소] "0" 설정
                { "MGCO_APTM_ODNO", "" },               // 운용사지정주문번호
                { "ORD_SVR_DVSN_CD", "0" }              // 주문서버구분코드
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;

        }

        public static DataTable GetOverseasOrderAllCncl(string excg_cd = "", string itm_no = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-nccs";
            string trID = "TTTS3018R"; // 모의투자 VTTS3018R
            DataTable currentData = new DataTable();

            if (string.IsNullOrEmpty(excg_cd)) // 해외거래소코드 필수
            {
                Console.WriteLine("해외거래소코드 확인요망!!!");
                return null;
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct }, // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd }, // 해외거래소코드
                { "SORT_SQN", "DS" }, // DS : 정순, 그외 : 역순
                { "CTX_AREA_FK200", FK100 }, // 페이징 처리
                { "CTX_AREA_NK200", NK100 } // 페이징 처리
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                currentData = Common.ConvertToDataTable(jobj);
                if (dataTable != null) {
                    dataTable.Merge(currentData);
                    trCont = res.Result.Headers.FirstOrDefault(i=>i.Key=="tr_cont").Value.FirstOrDefault();
                }
                else {
                    dataTable = currentData;
                }
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            FK100 = (string)jobj["ctx_area_fk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();
            NK100 = (string)jobj["ctx_area_nk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();

            if (trCont == "D" || trCont == "E")
            {
                Console.WriteLine("The End");
                int cnt = currentData.Rows.Count;

                if (cnt == 0)
                {
                    Console.WriteLine("미체결내역 없음");
                }
                else
                {
                    Console.WriteLine("미체결내역 있음");
                }

                foreach (DataRow row in currentData.Rows)
                {
                    Console.WriteLine(row["odno"]);
                    string r_odno = row["odno"].ToString();
                    var res_cncl = GetOverseasOrderRvseCncl("NASD", "", r_odno, "02");
                    Console.WriteLine(res_cncl);
                }

                return dataTable;

            }
            else if (trCont == "F" || trCont == "M")
            {
                Console.WriteLine("Call Next");
                Task.Delay(100);
                return GetOverseasOrderAllCncl(excg_cd, itm_no, "N", FK100, NK100, dataTable);
            }


            return dataTable;
        }

        public static DataTable GetOverseasInquireNccs(string excg_cd = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-nccs";
            string trID = "TTTS3018R"; // 모의투자 VTTS3018R
            DataTable currentData = new DataTable();

            if (string.IsNullOrEmpty(excg_cd)) // 해외거래소코드 필수
            {
                Console.WriteLine("해외거래소코드 확인요망!!!");
                return null;
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct }, // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd }, // 해외거래소코드
                { "SORT_SQN", "DS" }, // DS : 정순, 그외 : 역순
                { "CTX_AREA_FK200", FK100 }, // 페이징 처리
                { "CTX_AREA_NK200", NK100 } // 페이징 처리
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);


            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                currentData = Common.ConvertToDataTable(jobj);
                if (dataTable != null) {
                    dataTable.Merge(currentData);
                    trCont = res.Result.Headers.FirstOrDefault(i=>i.Key=="tr_cont").Value.FirstOrDefault();
                }
                else {
                    dataTable = currentData;
                }
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            FK100 = (string)jobj["ctx_area_fk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();
            NK100 = (string)jobj["ctx_area_nk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();

            if (trCont == "D" || trCont == "E")
            {
                Console.WriteLine("The End");
                int cnt = currentData.Rows.Count;
                if (cnt == 0)
                {
                    Console.WriteLine("미체결내역 없음");
                }
                else
                {
                    Console.WriteLine("미체결내역 있음");
                }

                return dataTable;

            }
            else if (trCont == "F" || trCont == "M")
            {
                Console.WriteLine("Call Next");
                Task.Delay(100);
                return GetOverseasInquireNccs(excg_cd, "N", FK100, NK100, dataTable);
            }

            return dataTable;

        }

        public static DataTable GetOverseasInquireBalance(string excg_cd = "", string crcy_cd = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-balance";
            string trID = "TTTS3012R"; // 모의투자 VTTS3012R

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct }, // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd }, // 해외거래소코드
                { "TR_CRCY_CD", crcy_cd }, // 거래통화코드
                { "CTX_AREA_FK200", FK100 }, // 페이징 처리
                { "CTX_AREA_NK200", NK100 } // 페이징 처리
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                DataTable current_data = Common.ConvertToDataTable(jobj);
                dataTable = current_data;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasInquireBalanceLst(string excg_cd = "", string crcy_cd = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-balance";
            string trID = "TTTS3012R"; // 모의투자 VTTS3012R
            DataTable currentData = new DataTable();

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct }, // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd }, // 해외거래소코드
                { "TR_CRCY_CD", crcy_cd }, // 거래통화코드
                { "CTX_AREA_FK200", FK100 }, // 페이징 처리
                { "CTX_AREA_NK200", NK100 } // 페이징 처리
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            // Append to the existing DataTable if it exists
            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                currentData = Common.ConvertToDataTable(jobj);
                if (dataTable != null) {
                    dataTable.Merge(currentData);
                    trCont = res.Result.Headers.FirstOrDefault(i=>i.Key=="tr_cont").Value.FirstOrDefault();
                }
                else {
                    dataTable = currentData;
                }
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            FK100 = (string)jobj["ctx_area_fk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();
            NK100 = (string)jobj["ctx_area_nk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();

            if (trCont == "D" || trCont == "E")
            {
                Console.WriteLine("The End");
                int cnt = currentData.Rows.Count;

                if (cnt == 0)
                {
                    Console.WriteLine("잔고내역 없음");
                }
                else
                {
                    Console.WriteLine("잔고내역 있음");
                }

                return dataTable;

            }
            else if (trCont == "F" || trCont == "M")
            {
                Console.WriteLine("Call Next");
                Task.Delay(100);
                return GetOverseasInquireBalanceLst(excg_cd, crcy_cd, "N", FK100, NK100, dataTable);
            }

            return dataTable;
        }

        /*
        ##############################################################################################
        # [해외주식] 주문/계좌 > 해외주식 주문체결내역[v1_해외주식-007]
        # 일정 기간의 해외주식 주문 체결 내역을 확인하는 API입니다.
        # 실전계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
        # 모의계좌의 경우, 한 번의 호출에 최대 15건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
        #
        # * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        # https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
        #
        # ※ 해외 거래소 운영시간(한국시간 기준)
        # 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        # 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        # 3) 상해 : 10:30 ~ 16:00
        # 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00
        ##############################################################################################
        # 해외주식 주문체결내역 List를 DataTable로 반환
        # Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
        # Output: DataTable (Option) output API 문서 참조 등
        */
        public static DataTable GetOverseasInquireCcnl(
            string pdno = "", string stDt = "", string edDt = "", string ordDv = "00", string ccldDv = "00", string excgCd = "%", string sort_sqn = "DS", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-ccnl";
            string trID = "TTTS3035R"; // 모의투자 VTTS3035R

            if (string.IsNullOrEmpty(stDt))
                stDt = DateTime.Today.ToString("yyyyMMdd");

            if (string.IsNullOrEmpty(edDt))
                edDt = DateTime.Today.ToString("yyyyMMdd");
            

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod },
                { "PDNO", pdno },
                { "ORD_STRT_DT", stDt },
                { "ORD_END_DT",  edDt },
                { "SLL_BUY_DVSN", ordDv },
                { "CCLD_NCCS_DVSN", ccldDv },
                { "OVRS_EXCG_CD", excgCd},
                { "SORT_SQN", sort_sqn },
                { "ORD_DT", "" },
                { "ORD_GNO_BRNO", "" },
                { "ODNO" , "" },
                { "CTX_AREA_FK200", FK100 },
                { "CTX_AREA_NK200", NK100 }
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj["output"]);
                if (dataTable != null) {
                    dataTable.Merge(currentData);
                    trCont = res.Result.Headers.FirstOrDefault(i=>i.Key=="tr_cont").Value.FirstOrDefault();

                }
                else {
                    dataTable = currentData;
                }
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            FK100 = (string)jobj["ctx_area_fk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();
            NK100 = (string)jobj["ctx_area_nk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();

            if (trCont == "D" || trCont == "E")
            {
                Console.WriteLine("The End");
                return dataTable;
            }
            else if (trCont == "F" || trCont == "M")
            {
                Console.WriteLine("Call Next");
                Task.Delay(100);
                return GetOverseasInquireCcnl(pdno, stDt, edDt, ordDv, ccldDv, excgCd, sort_sqn, "N", FK100, NK100, dataTable);
            }

            return dataTable;

        }

        /*
        ##############################################################################################
        # [해외주식] 주문/계좌 > 해외주식 체결기준현재잔고[v1_해외주식-008]
        # 해외주식 잔고를 체결 기준으로 확인하는 API 입니다.
        #
        # HTS(eFriend Plus) [0839] 해외 체결기준잔고 화면을 API로 구현한 사항으로 화면을 함께 보시면 기능 이해가 쉽습니다.
        #
        # (※모의계좌의 경우 output3(외화평가총액 등 확인 가능)만 정상 출력됩니다.
        # 잔고 확인을 원하실 경우에는 해외주식 잔고[v1_해외주식-006] API 사용을 부탁드립니다.)
        #
        # * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        # https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
        #
        # 해외주식 체결기준현재잔고 유의사항
        # 1. 해외증권 체결기준 잔고현황을 조회하는 화면입니다.
        # 2. 온라인국가는 수수료(국내/해외)가 반영된 최종 정산금액으로 잔고가 변동되며, 결제작업 지연등으로 인해 조회시간은 차이가 발생할 수 있습니다.
        #    - 아시아 온라인국가 : 매매일 익일    08:40 ~ 08:45분 경
        #    - 미국 온라인국가   : 당일 장 종료후 08:40 ~ 08:45분 경
        #   ※ 단, 애프터연장 참여 신청계좌는 10:30 ~ 10:35분 경(Summer Time : 09:30 ~ 09:35분 경)에 최종 정산금액으로 변동됩니다.
        # 3. 미국 현재가 항목은 주간시세 및 애프터시세는 반영하지 않으며, 정규장 마감 후에는 종가로 조회됩니다.
        # 4. 온라인국가를 제외한 국가의 현재가는 실시간 시세가 아니므로 주문화면의 잔고 평가금액 등과 차이가 발생할 수 있습니다.
        # 5. 해외주식 담보대출 매도상환 체결내역은 해당 잔고화면에 반영되지 않습니다.
        #    결제가 완료된 이후 외화잔고에 포함되어 반영되오니 참고하여 주시기 바랍니다.
        # 6. 외화평가금액은 당일 최초고시환율이 적용된 금액으로 실제 환전금액과는 차이가 있습니다.
        # 7. 미국은 메인 시스템이 아닌 별도 시스템을 통해 거래되므로, 18시 10~15분 이후 발생하는 미국 매매내역은 해당 화면에 실시간으로 반영되지 않으니 하단 내용을 참고하여 안내하여 주시기 바랍니다.
        #    [외화잔고 및 해외 유가증권 현황 조회]
        #    - 일반/통합증거금 계좌 : 미국장 종료 + 30분 후 부터 조회 가능
        #                             단, 통합증거금 계좌에 한해 주문금액은 외화잔고 항목에 실시간 반영되며, 해외 유가증권 현황은 반영되지
        #                             않아 해외 유가증권 평가금액이 과다 또는 과소 평가될 수 있습니다.
        #    - 애프터연장 신청계좌  : 실시간 반영
        #                             단, 시스템정산작업시간(23:40~00:10) 및 거래량이 많은 경우 메인시스템에 반영되는 시간으로 인해 차이가
        #                             발생할 수 있습니다.
        #    ※ 배치작업시간에 따라 시간은 변동될 수 있습니다.
        ##############################################################################################
        # 해외주식 체결기준현재잔고 List를 dataTable 으로 반환
        # Input: None (Option) 상세 Input값 변경이 필요한 경우 API문서 참조
        # Output: dataTable (Option) output API 문서 참조 등
        */
        public static DataTable GetOverseasInquirePresentBalance(string dv = "03", string dvsn = "01", string natn = "000", string mkt = "00", string inqr_dvsn = "00", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-present-balance";
            string trID = "CTRP6504R"; // 모의투자 VTRP6504R
            DataTable currentData = new DataTable();

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },         // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "WCRC_FRCR_DVSN_CD", dvsn },              // 원화외화구분코드 01 : 원화, 02 : 외화
                { "NATN_CD", natn },                        // 국가코드 000 전체, 840 미국, 344 홍콩, 156 중국, 392 일본, 704 베트남
                { "TR_MKET_CD", mkt },                      // 거래시장코드 00:전체 (API문서 참조)
                { "INQR_DVSN_CD", inqr_dvsn }               // 00 : 전체,01 : 일반해외주식,02 : 미니스탁
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                if (dv == "01") {
                    currentData = Common.ConvertToDataTable(jobj["output1"]);
                }
                else if (dv == "02") {
                    currentData = Common.ConvertToDataTable(jobj["output2"]);
                }
                else {
                    currentData = Common.ConvertToDataTable(jobj["output3"]);
                }
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }
 
        public static DataTable GetOverseasInquirePsamount(string dv = "03", string dvsn = "01", string natn = "000", string mkt = "00", string inqr_dvsn = "00", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-psamount";
            string trID = "TTTS3007R"; // 모의투자 VTTS3007R

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },         // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", dvsn },                  // 원화외화구분코드 01 : 원화, 02 : 외화
                { "OVRS_ORD_UNPR", natn },                 // 국가코드 000 전체, 840 미국, 344 홍콩, 156 중국, 392 일본, 704 베트남
                { "ITEM_CD", inqr_dvsn }                   // 00 : 전체,01 : 일반해외주식,02 : 미니스탁
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasDaytimeOrder(string ord_dv = "", string excg_cd = "", string itm_no = "", int qty = 0, double unpr = 0, string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/daytime-order";
            string trID;

            if (ord_dv == "buy")
            {
                trID = "TTTS6036U"; // 미국주간매수
            }
            else if (ord_dv == "sell")
            {
                trID = "TTTS6037U"; // 미국주간매도
            }
            else
            {
                Console.WriteLine("매수매도구분(ord_dv) 확인요망!!!");
                return null;
            }

            if (string.IsNullOrEmpty(excg_cd))
            {
                Console.WriteLine("해외거래소코드(excg_cd) 확인요망!!!");
                return null;
            }

            if (string.IsNullOrEmpty(itm_no))
            {
                Console.WriteLine("주문종목번호(itm_no 상품번호) 확인요망!!!");
                return null;
            }

            if (qty == 0)
            {
                Console.WriteLine("주문수량(qty) 확인요망!!!");
                return null;
            }

            if (unpr == 0)
            {
                Console.WriteLine("해외주문단가(unpr) 확인요망!!!");
                return null;
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },         // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd },                // 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스
                { "PDNO", itm_no },                         // 종목코드
                { "ORD_DVSN", "00" },                       // 주문구분 00:지정가 * 주간거래는 지정가만 가능
                { "ORD_QTY", qty.ToString() },              // 주문주식수
                { "OVRS_ORD_UNPR", unpr.ToString() },      // 해외주문단가
                { "CTAC_TLNO", "" },                        // 연락전화번호
                { "MGCO_APTM_ODNO", "" },                   // 운용사지정주문번호
                { "ORD_SVR_DVSN_CD", "0" }                  // 주문서버구분코드
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasDaytimeOrderRvseCncl(string excg_cd = "", string itm_no = "", string orgn_odno = "", string rvse_cncl_dvsn_cd = "", int qty = 0, double unpr = 0, string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/daytime-order-rvsecncl";
            string trID = "TTTS6038U"; // 미국주간정정취소

            if (string.IsNullOrEmpty(excg_cd))
            {
                Console.WriteLine("해외거래소코드(excg_cd) 확인요망!!!");
                return null;
            }

            if (string.IsNullOrEmpty(itm_no))
            {
                Console.WriteLine("주문종목번호(itm_no 상품번호) 확인요망!!!");
                return null;
            }

            if (string.IsNullOrEmpty(orgn_odno))
            {
                Console.WriteLine("원주문번호(orgn_odno) 확인요망!!!");
                return null;
            }

            if (!new[] { "01", "02" }.Contains(rvse_cncl_dvsn_cd))
            {
                Console.WriteLine("정정취소구분코드(rvse_cncl_dvsn_cd) 확인요망!!!"); // 정정:01. 취소:02
                return null;
            }

            if (rvse_cncl_dvsn_cd == "01" && unpr == 0)
            {
                Console.WriteLine("주문단가(unpr) 확인요망!!!");
                return null;
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },     // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd },            // 해외거래소코드 NASD:나스닥,NYSE:뉴욕,AMEX:아멕스,SEHK:홍콩,SHAA:중국상해,SZAA:중국심천,TKSE:일본,HASE:베트남하노이,VNSE:호치민
                { "PDNO", itm_no },                     // 종목번호(상품번호)
                { "ORGN_ODNO", orgn_odno },             // 원주문번호 정정 또는 취소할 원주문번호 (해외주식_주문 API ouput ODNO or 해외주식 미체결내역 API output ODNO 참고)
                { "RVSE_CNCL_DVSN_CD", rvse_cncl_dvsn_cd }, // 정정 : 01, 취소 : 02
                { "ORD_QTY", qty.ToString() },           // 주문수량	[잔량전부 취소/정정주문] "0" 설정 ( QTY_ALL_ORD_YN=Y 설정 ) [잔량일부 취소/정정주문] 취소/정정 수량
                { "OVRS_ORD_UNPR", unpr.ToString() },    // 해외주문단가 	[정정] 소수점 포함, 1주당 가격 [취소] "0" 설정
                { "CTAC_TLNO", "" },                    // 연락전화번호
                { "MGCO_APTM_ODNO", "" },               // 운용사지정주문번호
                { "ORD_SVR_DVSN_CD", "0" }              // 주문서버구분코드
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;

        }

        public static DataTable GetOverseasInquirePeriodProfit(string excg_cd = "", string crcy = "", string itm_no = "", string st_dt = "", string ed_dt = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-period-profit";
            string trID = "TTTS3039R";

            if (string.IsNullOrEmpty(st_dt))
            {
                st_dt = DateTime.Today.ToString("yyyyMMdd"); // 기간손익 시작일자 값이 없으면 현재일자
            }

            if (string.IsNullOrEmpty(ed_dt))
            {
                ed_dt = DateTime.Today.ToString("yyyyMMdd"); // 기간손익 종료일자 값이 없으면 현재일자
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },         // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd },                // 해외거래소코드, 공란:전체,NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
                { "NATN_CD", "" },                          // 국가코드 공란(Default)
                { "CRCY_CD", crcy },                        // 통화코드 공란:전체,USD:미국달러,HKD:홍콩달러,CNY:중국위안화,JPY:일본엔화,VND:베트남동
                { "PDNO", itm_no },                         // 상품번호 공란:전체
                { "INQR_STRT_DT", st_dt },                  // 조회시작일자 YYYYMMDD
                { "INQR_END_DT", ed_dt },                   // 조회종료일자 YYYYMMDD
                { "WCRC_FRCR_DVSN_CD", "02" },              // 원화외화구분코드 	01 : 외화, 02 : 원화
                { "CTX_AREA_FK200", FK100 },                // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
                { "CTX_AREA_NK200", NK100 }                 // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);

            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj["output2"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;

        }

        public static DataTable GetOverseasInquirePeriodProfitOutput1(string excg_cd = "", string crcy = "", string itm_no = "", string st_dt = "", string ed_dt = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-period-profit";
            string trID = "TTTS3039R";
            DataTable currentData = new DataTable();


            if (string.IsNullOrEmpty(st_dt))
            {
                st_dt = DateTime.Today.ToString("yyyyMMdd"); // 기간손익 시작일자 값이 없으면 현재일자
            }

            if (string.IsNullOrEmpty(ed_dt))
            {
                ed_dt = DateTime.Today.ToString("yyyyMMdd"); // 기간손익 종료일자 값이 없으면 현재일자
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },         // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "OVRS_EXCG_CD", excg_cd },                // 해외거래소코드, 공란:전체,NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
                { "NATN_CD", "" },                          // 국가코드 공란(Default)
                { "CRCY_CD", crcy },                        // 통화코드 공란:전체,USD:미국달러,HKD:홍콩달러,CNY:중국위안화,JPY:일본엔화,VND:베트남동
                { "PDNO", itm_no },                         // 상품번호 공란:전체
                { "INQR_STRT_DT", st_dt },                  // 조회시작일자 YYYYMMDD
                { "INQR_END_DT", ed_dt },                   // 조회종료일자 YYYYMMDD
                { "WCRC_FRCR_DVSN_CD", "02" },              // 원화외화구분코드 	01 : 외화, 02 : 원화
                { "CTX_AREA_FK200", FK100 },                // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
                { "CTX_AREA_NK200", NK100 }                 // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);

            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                currentData = Common.ConvertToDataTable(jobj["output1"]);
                if (dataTable != null) {
                    dataTable.Merge(currentData);
                    trCont = res.Result.Headers.FirstOrDefault(i=>i.Key=="tr_cont").Value.FirstOrDefault();

                }
                else {
                    dataTable = currentData;
                }
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            FK100 = (string)jobj["ctx_area_fk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();
            NK100 = (string)jobj["ctx_area_nk200"] is null ? "" : (string)jobj["ctx_area_fk200"].ToString();

            if (trCont == "D" || trCont == "E")
            {
                Console.WriteLine("The End");
                return dataTable;
            }
            else if (trCont == "F" || trCont == "M")
            {
                Console.WriteLine("Call Next");
                Task.Delay(100);
                return GetOverseasInquirePeriodProfitOutput1(excg_cd, crcy, itm_no, st_dt, ed_dt, "N", FK100, NK100, dataTable);
            }

            return dataTable;

        }

        // GET 타입
        public static DataTable GetOverseasInquireForeignMargin(string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/foreign-margin";
            string trID = "TTTC2101R";

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },         // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod } // 계좌상품코드 2자리
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj["output"]);
                dataTable = currentData.AsEnumerable().Where(row => !string.IsNullOrEmpty(row.Field<string>("crcy_cd"))).CopyToDataTable(); // 통화코드(crcy_cd) 값이 없는 경우 제외
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        // GET
        public static DataTable GetOverseasInquirePeriodTrans(string excg_cd = "", string dvsn = "00", string itm_no = "", string st_dt = "", string ed_dt = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-period-trans";
            string trID = "CTOS4001R";
            DataTable currentData = new DataTable();

            if (string.IsNullOrEmpty(st_dt))
            {
                st_dt = DateTime.Today.ToString("yyyyMMdd"); // 기간손익 시작일자 값이 없으면 현재일자
            }

            if (string.IsNullOrEmpty(ed_dt))
            {
                ed_dt = DateTime.Today.ToString("yyyyMMdd"); // 기간손익 종료일자 값이 없으면 현재일자
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },         // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "ERLM_STRT_DT", st_dt },                  // 조회시작일자 YYYYMMDD
                { "ERLM_END_DT", ed_dt },                   // 조회종료일자 YYYYMMDD
                { "OVRS_EXCG_CD", excg_cd },                // 해외거래소코드, 공란:전체,NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
                { "PDNO", itm_no },                         // 상품번호 공란:전체
                { "SLL_BUY_DVSN_CD", dvsn },                // 매도매수구분코드 00(전체), 01(매도), 02(매수)
                { "LOAN_DVSN_CD", "" },                     // 대출구분코드 	01 : 외화, 02 : 원화
                { "CTX_AREA_FK100", FK100 },                // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
                { "CTX_AREA_NK100", NK100 }                 // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);

            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0"))
            {
                currentData = Common.ConvertToDataTable(jobj["output1"]);
                if (dataTable != null) {
                    dataTable.Merge(currentData);
                    trCont = res.Result.Headers.FirstOrDefault(i=>i.Key=="tr_cont").Value.FirstOrDefault();
                }
                else {
                    dataTable = currentData;
                    trCont = res.Result.Headers.FirstOrDefault(i=>i.Key=="tr_cont").Value.FirstOrDefault();
                }
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            FK100 = (string)jobj["ctx_area_fk100"] is null ? "" : (string)jobj["ctx_area_fk100"].ToString();
            NK100 = (string)jobj["ctx_area_nk100"] is null ? "" : (string)jobj["ctx_area_fk100"].ToString();

            if (trCont == "D" || trCont == "E")
            {
                Console.WriteLine("The End");

                int cnt = currentData.Rows.Count;

                if (cnt == 0)
                {
                    Console.WriteLine("잔고내역 없음");
                }
                else
                {
                    Console.WriteLine("잔고내역 있음");
                }

                return dataTable;
            }
            else if (trCont == "F" || trCont == "M")
            {
                Console.WriteLine("Call Next");
                Task.Delay(100);
                return GetOverseasInquirePeriodTrans(excg_cd, dvsn, itm_no, st_dt, ed_dt, "N", FK100, NK100, dataTable);
            }

            return dataTable;
        }


        public static DataTable GetOverseasInquirePeriodTransOutput2(string excg_cd = "", string dvsn = "00", string itm_no = "", string st_dt = "", string ed_dt = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-period-trans";
            string trID = "CTOS4001R";

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct },  // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod },  // 계좌상품코드 2자리
                { "ERLM_STRT_DT", st_dt },  // 조회시작일자 YYYYMMDD
                { "ERLM_END_DT", ed_dt },  // 조회종료일자 YYYYMMDD
                { "OVRS_EXCG_CD", excg_cd },  // 해외거래소코드, 공란:전체,NASD:미국,SEHK:홍콩,SHAA:중국,TKSE:일본,HASE:베트남
                { "PDNO", itm_no },  // 상품번호 공란:전체
                { "SLL_BUY_DVSN_CD", dvsn },  // 매도매수구분코드 00(전체), 01(매도), 02(매수)
                { "LOAN_DVSN_CD", "" },  // 대출구분코드 	01 : 외화, 02 : 원화
                { "CTX_AREA_FK100", FK100 },  // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK100 값 : 다음페이지 조회시(2번째부터)
                { "CTX_AREA_NK100", NK100 }  // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK100 값 : 다음페이지 조회시(2번째부터)
            };

            var res = Common.UrlFetch(paramsDict, url, trID, trCont, null, false);

            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                var currentData = Common.ConvertToDataTable(jobj["output2"]);
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasInquirePaymtStdrBalance(string dv = "03", string dt = "", string dvsn = "01", string inqrDvsn = "00", string trCont = "", string fk100 = "", string nk100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/trading/inquire-paymt-stdr-balance";
            string trId = "CTRP6010R";
            DataTable currentData = new DataTable();

            if (string.IsNullOrEmpty(dt))
            {
                dt = DateTime.Today.ToString("yyyyMMdd"); // 기본날짜 = 당일
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "CANO", Common.GetTREnv().my_acct }, // 종합계좌번호 8자리
                { "ACNT_PRDT_CD", Common.GetTREnv().my_prod }, // 계좌상품코드 2자리
                { "BASS_DT", dt }, // 기준일자(YYYYMMDD)
                { "WCRC_FRCR_DVSN_CD", dvsn }, // 원화외화구분코드 01 : 원화, 02 : 외화
                { "INQR_DVSN_CD", inqrDvsn } // 00 : 전체,01 : 일반해외주식,02 : 미니스탁
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                
                if (dv == "01")
                {
                    currentData = Common.ConvertToDataTable(jobj["Output1"]);
                }
                else if (dv == "02")
                {
                    currentData = Common.ConvertToDataTable(jobj["Output2"]);
                }
                else
                {
                    currentData = Common.ConvertToDataTable(jobj["Output3"]);
                }
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceQuotPrice(string excd = "", string itmNo = "", string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/price";
            string trId = "HHDFS00000300"; // 해외주식 현재체결가

            var paramsDict = new Dictionary<string, object>
            {
                { "AUTH", "" }, // 사용자권한정보 : 사용안함
                { "EXCD", excd }, // 거래소코드
                { "SYMB", itmNo } // 종목번호
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = Common.ConvertToDataTable(jobj["output"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceQuotDailyPrice(string excd = "", string itmNo = "", string gubn = "", string bymd = "", string modp = "0", string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/dailyprice";
            string trId = "HHDFS76240000"; // 해외주식 기간별시세

            if (string.IsNullOrEmpty(bymd))
            {
                bymd = DateTime.Today.ToString("yyyyMMdd"); // Current date if no date is provided
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "AUTH", "" }, // (사용안함) 사용자권한정보
                { "EXCD", excd }, // 거래소코드
                { "SYMB", itmNo }, // 종목번호
                { "GUBN", gubn }, // 일/주/월구분
                { "BYMD", bymd }, // 조회기준일자(YYYYMMDD)
                { "MODP", modp }, // 수정주가반영여부
                { "KEYB", "" } // (사용안함) NEXT KEY BUFF
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = Common.ConvertToDataTable(jobj["output2"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceQuotInquireDailyPrice(string div = "N", string itmNo = "", string stDt = "", string edDt = "", string period = "D", string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice";
            string trId = "FHKST03030100"; // 해외주식 종목/지수/환율기간별시세(일/주/월/년)

            if (string.IsNullOrEmpty(stDt))
            {
                stDt = DateTime.Today.ToString("yyyyMMdd");// Current date if no start date is provided
            }
            if (string.IsNullOrEmpty(edDt))
            {
                edDt = DateTime.Today.ToString("yyyyMMdd"); // Current date if no end date is provided
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "FID_COND_MRKT_DIV_CODE", div }, // 시장 분류 코드
                { "FID_INPUT_ISCD", itmNo }, // 종목번호
                { "FID_INPUT_DATE_1", stDt }, // 시작일자(YYYYMMDD)
                { "FID_INPUT_DATE_2", edDt }, // 종료일자(YYYYMMDD)
                { "FID_PERIOD_DIV_CODE", period } // 기간분류코드
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result); 

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = Common.ConvertToDataTable(jobj["output1"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceQuotInquireDailyChartPrice(string div = "N", string itmNo = "", string stDt = "", string edDt = "", string period = "D", string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice";
            string trId = "FHKST03030100"; // 해외주식 종목/지수/환율기간별시세(일/주/월/년)

            if (string.IsNullOrEmpty(stDt))
            {
                stDt = DateTime.Today.ToString("yyyyMMdd"); // Current date if no start date is provided
            }
            if (string.IsNullOrEmpty(edDt))
            {
                edDt = DateTime.Today.ToString("yyyyMMdd"); // Current date if no end date is provided
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "FID_COND_MRKT_DIV_CODE", div }, // 시장 분류 코드
                { "FID_INPUT_ISCD", itmNo }, // 종목번호
                { "FID_INPUT_DATE_1", stDt }, // 시작일자(YYYYMMDD)
                { "FID_INPUT_DATE_2", edDt }, // 종료일자(YYYYMMDD)
                { "FID_PERIOD_DIV_CODE", period } // 기간분류코드
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result); 

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = Common.ConvertToDataTable(jobj["output2"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceQuotInquireSearch(string div = "02", string excd = "", string prSt = "", string prEn = "", string rateSt = "", string rateEn = "", string volSt = "", string volEn = "",
            string perSt = "", string perEn = "", string epsSt = "", string epsEn = "", string amtSt = "", string amtEn = "", string sharSt = "",
            string sharEn = "", string valxSt = "", string valxEn = "", string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/inquire-search";
            string trId = "HHDFS76410000"; // [해외주식] 기본시세 > 해외주식조건검색

            var paramsDict = new Dictionary<string, object>
            {
                { "AUTH", "" }, // (사용안함)사용자권한정보(Null 값 설정)
                { "EXCD", excd }, // 거래소코드
                { "CO_YN_PRICECUR", (string.IsNullOrEmpty(prSt) || string.IsNullOrEmpty(prEn)) ? "" : "1" }, // 현재가선택조건
                { "CO_ST_PRICECUR", prSt }, // 현재가시작범위가
                { "CO_EN_PRICECUR", prEn }, // 현재가끝범위가
                { "CO_YN_RATE", (string.IsNullOrEmpty(rateSt) || string.IsNullOrEmpty(rateEn)) ? "" : "1" }, // 등락율선택조건
                { "CO_ST_RATE", rateSt }, // 등락율시작율
                { "CO_EN_RATE", rateEn }, // 등락율끝율
                { "CO_YN_VOLUME", (string.IsNullOrEmpty(volSt) || string.IsNullOrEmpty(volEn)) ? "" : "1" }, // 거래량선택조건
                { "CO_ST_VOLUME", volSt }, // 거래량시작량
                { "CO_EN_VOLUME", volEn }, // 거래량끝량
                { "CO_YN_PER", (string.IsNullOrEmpty(perSt) || string.IsNullOrEmpty(perEn)) ? "" : "1" }, // PER선택조건
                { "CO_ST_PER", perSt }, // PER시작
                { "CO_EN_PER", perEn }, // PER끝
                { "CO_YN_EPS", (string.IsNullOrEmpty(epsSt) || string.IsNullOrEmpty(epsEn)) ? "" : "1" }, // EPS선택조건
                { "CO_ST_EPS", epsSt }, // EPS시작
                { "CO_EN_EPS", epsEn }, // EPS끝
                { "CO_YN_AMT", (string.IsNullOrEmpty(amtSt) || string.IsNullOrEmpty(amtEn)) ? "" : "1" }, // 거래대금선택조건
                { "CO_ST_AMT", amtSt }, // 거래대금시작금
                { "CO_EN_AMT", amtEn }, // 거래대금끝금
                { "CO_YN_SHAR", (string.IsNullOrEmpty(sharSt) || string.IsNullOrEmpty(sharEn)) ? "" : "1" }, // 발행주식수선택조건
                { "CO_ST_SHAR", sharSt }, // 발행주식시작수
                { "CO_EN_SHAR", sharEn }, // 발행주식끝수
                { "CO_YN_VALX", (string.IsNullOrEmpty(valxSt) || string.IsNullOrEmpty(valxEn)) ? "" : "1" }, // 시가총액선택조건
                { "CO_ST_VALX", valxSt }, // 시가총액시작액
                { "CO_EN_VALX", valxEn }, // 시가총액끝액
                { "KEYB", "" } // (사용안함)NEXT KEY BUFF
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result); 

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = (div == "01") ? Common.ConvertToDataTable(jobj["output2"]) : Common.ConvertToDataTable(jobj["output1"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceQuotCountriesHoliday(string dt = "", string trCont = "", string FK100 = "", string NK100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-stock/v1/quotations/countries-holiday";
            string trId = "CTOS5011R"; // [해외주식] 기본시세 > 해외결제일자조회
            DataTable currentData = new DataTable();

            if (string.IsNullOrEmpty(dt))
            {
                dt = DateTime.Today.ToString("yyyyMMdd"); // Current date if no date is provided
            }

            var paramsDict = new Dictionary<string, object>
            {
                { "TRAD_DT", dt }, // 기준일자(YYYYMMDD)
                { "CTX_AREA_FK", FK100 }, // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_FK 값
                { "CTX_AREA_NK", NK100 } // 공란 : 최초 조회시 이전 조회 Output CTX_AREA_NK 값
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont, null, false); // API 호출
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result);

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다"))
            {
                currentData = Common.ConvertToDataTable(jobj["output"]);
                if (dataTable != null) {
                    dataTable.Merge(currentData);
                    trCont = res.Result.Headers.FirstOrDefault(i=>i.Key=="tr_cont").Value.FirstOrDefault();
                }
                else {
                    dataTable = currentData;
                }
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            FK100 = (string)jobj["CTX_AREA_FK"] is null ? "" : (string)jobj["CTX_AREA_FK"].ToString();
            NK100 = (string)jobj["CTX_AREA_NK"] is null ? "" : (string)jobj["CTX_AREA_NK"].ToString();

            if (trCont == "D" || trCont == "E")
            {
                Console.WriteLine("The End");
                return dataTable;

            }
            else if (trCont == "F" || trCont == "M")
            {
                Console.WriteLine("Call Next");
                Task.Delay(100); // Delay for system stability
                return GetOverseasPriceQuotCountriesHoliday(dt, "N", FK100, NK100, dataTable);
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceQuotPriceDetail(string excd = "", string itmNo = "", string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/price-detail";
            string trId = "HHDFS76200200"; // 해외주식 현재가상세

            var paramsDict = new Dictionary<string, object>
            {
                { "AUTH", "" }, // 시장 분류 코드
                { "EXCD", excd }, // 종목번호
                { "SYMB", itmNo } // 종목번호
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result); 

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = Common.ConvertToDataTable(jobj["output"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceQuotInquireTimeItemChartPrice(string div = "02", string excd = "", string itmNo = "", string nmin = "", string pinc = "0", string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/inquire-time-itemchartprice";
            string trId = "HHDFS76950200"; // 해외주식 해외주식분봉조회

            var paramsDict = new Dictionary<string, object>
            {
                { "AUTH", "" }, // 시장 분류 코드
                { "EXCD", excd }, // 거래소코드
                { "SYMB", itmNo }, // 종목코드
                { "NMIN", nmin }, // 분갭 분단위
                { "PINC", pinc }, // 전일포함여부
                { "NEXT", "" }, // (사용안함)다음여부
                { "NREC", "120" }, // 요청갯수 레코드요청갯수 (최대 120)
                { "FILL", "" }, // (사용안함)미체결채움구분
                { "KEYB", "" } // (사용안함)NEXT KEY BUFF
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result); 

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = (div == "02") ? Common.ConvertToDataTable(jobj["output2"]) : Common.ConvertToDataTable(jobj["output1"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }
        public static DataTable GetOverseasPriceQuotInquireTimeIndexChartPrice(string div = "01", string code = "N", string iscd = "", string tmDv = "0", string inc = "N", string trCont = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice";
            string trId = "FHKST03030200"; // 해외주식 해외지수분봉조회

            var paramsDict = new Dictionary<string, object>
            {
                { "FID_COND_MRKT_DIV_CODE", code }, // 시장 분류 코드
                { "FID_INPUT_ISCD", iscd }, // 종목코드
                { "FID_HOUR_CLS_CODE", tmDv }, // 시간 구분 코드
                { "FID_PW_DATA_INCU_YN", inc } // 과거 데이터 포함 여부
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result); 

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = (div == "02") ? Common.ConvertToDataTable(jobj["output2"]) : Common.ConvertToDataTable(jobj["output1"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceSearchInfo(string itmNo = "", string prdtTypeCd = "", string trCont = "", string fk100 = "", string nk100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/search-info";
            string trId = "CTPF1702R"; // 해외주식 상품기본정보

            var paramsDict = new Dictionary<string, object>
            {
                { "PDNO", itmNo }, // 종목번호
                { "PRDT_TYPE_CD", prdtTypeCd } // 종목유형
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont, null, false);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result); 

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = Common.ConvertToDataTable(jobj["output"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        }

        public static DataTable GetOverseasPriceInquireAskingPrice(string div = "", string excd = "", string itmNo = "", string trCont = "", string fk100 = "", string nk100 = "", DataTable? dataTable = null)
        {
            string url = "/uapi/overseas-price/v1/quotations/inquire-asking-price";
            string trId = "HHDFS76200100"; // 해외주식 현재가 10호가

            var paramsDict = new Dictionary<string, object>
            {
                { "AUTH", "" }, // (사용안함) 공백
                { "EXCD", excd }, // 거래소코드
                { "SYMB", itmNo } // 종목코드
            };

            var res = Common.UrlFetch(paramsDict, url, trId, trCont);
            var jsonResponse = res.Result.Content.ReadAsStringAsync();
            JObject jobj = JsonConvert.DeserializeObject<JObject>(jsonResponse.Result); 

            if (((String)jobj["rt_cd"]).Equals("0") && !((String)jobj["msg1"]).Contains("조회할 자료가 없습니다")){
                var currentData = (div == "01") ? Common.ConvertToDataTable(jobj["output1"]) : (div == "02") ? Common.ConvertToDataTable(jobj["output2"]) : Common.ConvertToDataTable(jobj["output3"]);
                dataTable = currentData;
            }
            else
            {
                Console.WriteLine(jobj["msg_cd"] + "," + jobj["msg1"]);
                dataTable = null;
            }

            return dataTable;
        } 

    }
}