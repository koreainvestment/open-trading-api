/*****************************************************************************
 * 해외종목코드정보(미국,중국,일본,홍콩,베트남)
 ****************************************************************************/
struct  mastcode {
    char    ncod[2+1];  /* National code        */
    char    exid[3+1];  /* Exchange id          */
    char    excd[3+1];  /* Exchange code        */
    char    exnm[16+1]; /* Exchange name        */
    char    symb[16+1]; /* Symbol               */
    char    rsym[16+1]; /* realtime symbol      */
    char    knam[64+1]; /* Korea name           */
    char    enam[64+1]; /* English name         */
    char    stis[1+1];  /* Security type        */
                        /* 1:Index              */
                        /* 2:Stock              */
                        /* 3:ETP(ETF)           */
                        /* 4:Warrant            */
    char    curr[4+1];  /* currency             */
    char    zdiv[1+1];  /* float position       */
    char    ztyp[1+1];  /* data type            */
    char    base[12+1]; /* base price           */
    char    bnit[8+1];  /* Bid order size       */
    char    anit[8+1];  /* Ask order size       */
    char    mstm[4+1];  /* market start time(HHMM)  */
    char    metm[4+1];  /* market end time(HHMM)    */
    char    isdr[1+1];  /* DR 여부  :Y, N       */
    char    drcd[2+1];  /* DR 국가코드          */
    char    icod[4+1];  /* 업종분류코드         */
    char    sjong[1+1]; /* 지수구성종목 존재 여부 */
                        /*   0:구성종목없음      */
                        /*   1:구성종목있음      */
    char    ttyp[1+1];  /* Tick size Type        */
    char    etyp[3+1]; /* 001: ETF 002: ETN 003: ETC 004: Others 005: VIX Underlying ETF 006: VIX Underlying ETN*/
    char    ttyp_sb[3+1]; /* Tick size type 상세 (ttyp 9일 경우 사용) : 런던 제트라 유로넥스트  */
};
