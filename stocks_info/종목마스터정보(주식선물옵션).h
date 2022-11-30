/*****************************************************************************
 * 주식 선물/옵션 종목 마스터파일(fo_stk_code_mts.mst) 헤더정보
 ****************************************************************************/
typedef struct
{
    char    info_type[1];           /* 1:코스피 주식선물 2:코스피 주식선물 SP 	*/
									/* 3:코스닥 주식선물 4:코스닥 주식선물 SP 	*/
                                    /* 5:주식 콜옵션 6:주식 풋옵션              */
    char    shrn_iscd[SZ_SHRNCODE]; /* 단축코드                                 */
    char    stnd_iscd[SZ_STNDCODE]; /* 표준코드                                 */
    char    kor_name[SZ_KORNAME];   /* 한글종목명                               */
    char    atm_cls_code[ 1];       /* ATM구분(1:ATM,2:ITM,3:OTM)               */
    char    acpr[8];                /* 행사가                                   */
    char    mmsc_cls_code[1];       /* 월물구분코드 (0:연결선물, 1:최근월물     */
                                    /* 2:차근월물 3:차차근월물 4:차차차근월물   */
    char    unas_shrn_iscd[SZ_SHRNCODE];   /* 기초자산 단축코드                 */
    char    unas_kor_name[SZ_KORNAME];     /* 기초자산 명                       */
} ST_FO_STK_CODE;