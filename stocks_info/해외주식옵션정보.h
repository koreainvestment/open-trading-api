/*****************************************************************************
 *  해외 선물옵션 파일 구조 (fostkcode.mst)
 ****************************************************************************/
typedef struct ST_FOSTKCODE_TBL
{
    char sSrsCd      [  32]; /* 종목코드    (UNIQ-KEY)       */
    char    sAutoOrdGnrlYN[  1];    /* 서버자동주문 가능 종목 여부 */
    char    sAutoOrdTwapYN[  1];    /* 서버자동주문 TWAP 가능 종목 여부 */
    char    sAutoOrdEcnmYN[  1];    /* 서버자동 경제지표 주문 가능 종목 여부 */
    char    sExchSubCd    [  2];    /* 서브 거래소 코드 2019.12.27           */
                                    /*  10:ASX    20:BALTIC   30:BMF      40:CBOE   */
                                    /*  50:CME    51:CME_CBOT 52:CME_NYMEX 53:CME_COMEX */
                                    /*  60:EUREX  70:FTX      80:HKEx             */
                                    /*  90:ICE_US 91:ICE_금융 92:ICE_상품 93:ICE_SG */
                                    /*  A0:ISE    B0:ITA      C0:JSE      D0:KCBT   */
                                    /*  E0:LBMA   F0:LME      G0:MDEX     H0:MDX    */
                                    /*  I0:MEFF   J0:NYSE     K0:OSE      L0:SGX    */
                                    /*  M0:SSE    N0:TFEX     O0:TMX      P0:HNX */
    char    sFiller      [  45];    /* 필러                         */
 char sSeriesKrNm  [  50]; /* 종목한글명                   */
 char sExchCd      [  10]; /* 거래소코드                   */
 char sMrktCd      [  10]; /* 품목코드                     */
 char sClasCd      [   3]; /* 품목종류                     */
                                 /* 1: 지수옵션                  */
                                 /* 2: 주식옵션 (M)              */
                                 /* 3: 현물옵션                  */
                                 /* 4: 선물옵션                  */
                                 /* 5: 주식옵션 (W)              */
 char sDispDesz    [   5]; /* 출력 소수점                  */
 char sCalcDesz    [   5]; /* 계산 소수점                  */
 char sTickSz      [  14]; /* 틱사이즈                     */
 char sTickVal     [  14]; /* 틱가치                       */
 char sCtrtSz      [  10]; /* 계약크기                     */
 char sDispDigit   [   4]; /* 가격표시진법                 */
 char sMultiplier  [  10]; /* 환산승수                     */
 char    sSymbol      [   1];    /* 옵션 구분 C, P               */
 char    sStkPrc      [  20];    /* Strike Price                 */
    char    sUndrInstr   [  10];    /* 관련선물코드                 */
                                    /*   해외선물 품목 코드         */
                                    /* 주식옵션인 경우 거래소 코드  */
                                    /*   ex: NAS, NYS, AMS          */
    char    sUndrAsset   [  32];    /* 관련선물종목                 */
                                    /*   해외선물 기초자산 종목코드 */
                                    /* 주식옵션인 경우 Ticker 코드  */
                                    /*   AAPL, TSLA                 */
    char    sRefrAsset   [  32];    /* 참조자산 Index등             */
                                    /*   지수인경우 지수명          */
                                    /*   해외선물인경우 관련 선물 종목코드 */
 char    sIncTickPrc  [  19];    /* 틱증가기준가                 */
    char    sIncTickSz   [   5];    /* 틱증가배수                   */
    char    sYearMon     [   6];    /* 년월                         */
    char    sAtmFlg      [   1];    /* A: ATM, I:ITM, O:OTM         */
    char    sNearFlg     [   1];    /* 근월물여부 0:원월물 1:근월물 */
} FOSTKCODE_TBL;