/*****************************************************************************
 *  코넥스 종목 코드 파일 구조
 ****************************************************************************/
typedef struct
{
    char    mksc_shrn_iscd[SZ_SHRNCODE];        /* 단축코드                                     */
    char    stnd_iscd[SZ_STNDCODE];             /* 표준코드                                     */
    char    hts_kor_isnm[SZ_KORNAME];           /* 한글종목명                                   */
    char    scrt_grp_cls_code[2];               /* 증권그룹구분코드                             */
                                                /* KN:코넥스                                    */
    char    stck_sdpr[9];                       /* 주식 기준가                                  */
    char    frml_mrkt_deal_qty_unit[5];         /* 정규 시장 매매 수량 단위                     */
    char    ovtm_mrkt_deal_qty_unit[5];         /* 시간외 시장 매매 수량 단위                   */
    char    trht_yn[1];                         /* 거래정지 여부                                */
    char    sltr_yn[1];                         /* 정리매매 여부                                */
    char    mang_issu_yn[1];                    /* 관리 종목 여부                               */
    char    mrkt_alrm_cls_code[2];              /* 시장 경고 구분 코드 (00:해당없음 01:투자주의 */
                                                /* 02:투자경고 03:투자위험                      */
    char    mrkt_alrm_risk_adnt_yn[1];          /* 시장 경고위험 예고 여부                      */
    char    insn_pbnt_yn[1];                    /* 불성실 공시 여부                             */
    char    byps_lstn_yn[1];                    /* 우회 상장 여부                               */
    char    flng_cls_code[2];                   /* 락구분 코드 									*/
												/* 00:해당사항없음 01:권리락       				*/
                                                /* 02:배당락 03:분배락 04:권배락 05:중간배당락  */
                                                /* 06:권리중간배당락 99:기타                    */
                                                /* SW,SR,EW는 미해당(미해당의경우 SPACE)        */
    char    fcam_mod_cls_code[2];               /* 액면가 변경 구분 코드 (00:해당없음           */
                                                /* 01:액면분할 02:액면병합 99:기타)             */
    char    icic_cls_code[2];                   /* 증자 구분 코드 (00:해당없음 01:유상증자      */
                                                /* 02:무상증자 03:유무상증자 99:기타)           */
    char    marg_rate[3];                       /* 증거금 비율                                  */
    char    crdt_able[1];                       /* 신용주문 가능 여부                           */
    char    crdt_days[3];                       /* 신용기간                                     */
    char    prdy_vol[12];                       /* 전일 거래량                                  */
    char    stck_fcam[12];                      /* 주식 액면가                                  */
    char    stck_lstn_date[8];                  /* 주식 상장 일자                               */
    char    lstn_stcn[15];                      /* 상장 주수(천)                                */
    char    cpfn[21];                           /* 자본금                                       */
    char    stac_month[2];                      /* 결산 월                                      */
    char    po_prc[7];                          /* 공모 가격                                    */
    char    prst_cls_code[1];                   /* 우선주 구분 코드 (0:해당없음(보통주)         */
                                                /* 1:구형우선주 2:신형우선주)                   */
    char    ssts_hot_yn[1];                     /* 공매도과열종목여부  							*/
    char    stange_runup_yn[1];                 /* 이상급등종목여부 							*/
    char    krx300_issu_yn[1];                  /* KRX300 종목 여부 (Y/N) (실제적으로 필러)     */
    char    sale_account[9];                    /* 매출액                                       */
    char    bsop_prfi[9];                       /* 영업이익                                     */
    char    op_prfi[9];                         /* 경상이익                                     */
    char    thtr_ntin[5];                       /* 단기순이익                                   */
    char    roe[9];                             /* ROE(자기자본이익률)                          */
    char    base_date[8];                       /* 기준년월                                     */
    char    prdy_avls_scal[9];                  /* 전일기준 시가총액 (억)                       */
    char    co_crdt_limt_over_yn[1];            /* 회사신용한도초과여부                         */
    char    secu_lend_able_yn[1];               /* 담보대출가능여부                             */
    char    stln_able_yn[1];                    /* 대주가능여부                                 */
}   ST_KNX_CODE;
