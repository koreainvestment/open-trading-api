/*****************************************************************************
 * ELW 종목 코드 파일 구조
 ****************************************************************************/
typedef struct
{
	char	mksc_shrn_iscd			[SZ_SHRNCODE];	/* 단축코드                */
	char	stnd_iscd				[SZ_STNDCODE];	/* 표준코드                */
	char	hts_kor_isnm			[SZ_KORNAME];	/* 한글종목명              */
	char	elw_nvlt_optn_cls_code  [1];			/* ELW권리형태             */
													/* 0 : 표준옵션            */
													/* 1 : 디지털옵현          */
													/* 2: 조기종료 옵션        */
	char	elw_ko_barrier			[13];			/* ELW조기종료발생기준가격 */
	char	bskt_yn                 [1];            /* 바스켓 여부 (Y/N)       */
	char    unas_iscd1              [SZ_SHRNCODE];  /* 기초자산코드            */
	char    unas_iscd2              [SZ_SHRNCODE];  /* 기초자산코드            */
	char    unas_iscd3              [SZ_SHRNCODE];  /* 기초자산코드            */
	char    unas_iscd4              [SZ_SHRNCODE];  /* 기초자산코드            */
	char    unas_iscd5              [SZ_SHRNCODE];  /* 기초자산코드            */
	char    elw_pblc_istu_name      [SZ_KORNAME];   /* 발행사 한글 종목명      */
	char	elw_pblc_mrkt_prtt_no   [5];	        /* 발행사코드              */
	char    acpr                    [9];            /* 행사가                  */
	char    stck_last_tr_month      [8];            /* 최종거래일              */
	char    rmnn_dynu               [4];            /* 잔존 일수               */
    char    rght_type_cls_code      [1];            /* 권리 유형 구분 코드     */
                                                    /* 'C':콜 'E':기타 'P':풋  */
	char    paym_date               [8];            /* 지급일                  */
	char    prdy_avls               [9];            /* 전일시가총액(억)        */
	char    lstn_stcn               [15];           /* 상장주수(천)            */
	char    mrkt_prtt_no1           [5];            /* 시장 참가자 번호1       */
	char    mrkt_prtt_no2           [5];            /* 시장 참가자 번호2       */
	char    mrkt_prtt_no3           [5];            /* 시장 참가자 번호3       */
	char    mrkt_prtt_no4           [5];            /* 시장 참가자 번호4       */
	char    mrkt_prtt_no5           [5];            /* 시장 참가자 번호5       */
	char    mrkt_prtt_no6           [5];            /* 시장 참가자 번호6       */
	char    mrkt_prtt_no7           [5];            /* 시장 참가자 번호7       */
	char    mrkt_prtt_no8           [5];            /* 시장 참가자 번호8       */
	char    mrkt_prtt_no9           [5];            /* 시장 참가자 번호9       */
	char    mrkt_prtt_no10          [5];            /* 시장 참가자 번호10      */
} ST_ELW_CODE;
