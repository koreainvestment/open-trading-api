/*****************************************************************************
 * 지수 선물/옵션 종목
 ****************************************************************************/
typedef struct
{
    char    info_type[1];           /* 1:지수선물 2:지수SP 3:스타선물 4:스타SP  */
                                    /* 5:지수콜옵션 6:지수풋옵션                */
                                    /* 7:변동성선물 8:변동성SP                  */
                                    /* 9:섹터선물 A:섹터SP                      */
                                    /* B:미니선물 C:미니SP                      */
                                    /* D:미니콜옵션 E:미니풋옵션                */
					                /* J:코스닥150콜옵션 K:코스닥150풋옵션      */
                                    /* L:위클리콜옵션 M:위클리풋옵션            */
    char    shrn_iscd[SZ_SHRNCODE]; /* 단축코드                                 */
    char    stnd_iscd[SZ_STNDCODE]; /* 표준코드                                 */
    char    kor_name[SZ_KORNAME];   /* 한글종목명                               */
	char	atm_cls_code[ 1];		/* ATM구분(1:ATM,2:ITM,3:OTM)               */
    char    acpr[8];                /* 행사가                                   */
	char	mmsc_cls_code[1];       /* 월물구분코드 (0:연결선물, 1:최근월물     */
									/* 2:차근월물 3:차차근월물 4:차차차근월물   */
	char	unas_shrn_iscd[SZ_SHRNCODE];   /* 기초자산 단축코드                 */
	char	unas_kor_name[SZ_KORNAME];     /* 기초자산 명                       */
} ST_FO_IDX_CODE;
