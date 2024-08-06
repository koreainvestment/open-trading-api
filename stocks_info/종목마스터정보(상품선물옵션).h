/*****************************************************************************
 * 상품 선물/옵션 종목
 ****************************************************************************/
typedef struct
{
	char	com_type[1];			/* 상품구분                                 */
									/* 1:금리 2:통화 3:상품                     */
    char    info_type[1];           /* 1:선물 2:SP선물                          */
									/* 5:콜옵션 6:풋옵션                        */
    char    shrn_iscd[SZ_SHRNCODE]; /* 단축코드  (SZ_SHRNCODE=9)                */
    char    stnd_iscd[SZ_STNDCODE]; /* 표준코드  (SZ_STNDCODE=12)                */
    char    kor_name[SZ_KORNAME];   /* 한글종목명 (SZ_KORNAME=40)                */
	char	atm_cls_code[ 1];		/* ATM구분(1:ATM,2:ITM,3:OTM)               */
    char    acpr[8];                /* 행사가                                   */
	char	mmsc_cls_code[1];       /* 월물구분코드 (0:연결선물, 1:최근월물     */
									/* 2:차근월물 3:차차근월물 4:차차차근월물   */
									/* SP 는 무조건 1                           */
	char	prod_no[3];             /* 기초자산 단축코드                        */
									/* B03 : 3년국채       B05 : 5년국채        */
									/* B10 : 10년국채      MSB : 통안증권       */
									/* USD : 미국달러      JPY : 엔             */
									/* EUR : 유로          GLD : 금             */
									/* LHG : 돈육          CMU : CME미국달러    */
									/* RFR : 3개월무위험금리                    */
	char	prod_name[SZ_KORNAME];  /* 기초자산 명 (SZ_KORNAME=40)               */
} ST_FO_COM_CODE;