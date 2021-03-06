/*****************************************************************************
 *  해외 코드 파일 구조
 ****************************************************************************/
typedef struct
{
    char    cls_code[1];                        /* 구분코드                                     */
                                                /* W : 세계주요지수                             */
                                                /* P : 미국지수                                 */
                                                /* Q : 미국종목                                 */
                                                /* H : 세계주요종목                             */
                                                /* D : 미국상장국내기업                         */
                                                /* G : 유럽상장국내기업                         */
                                                /* F : CME선물                                  */
                                                /* M : 반도체                                   */
                                                /* X : 환율                                     */
                                                /* C : 상품선물                                 */
                                                /* R : 국내금리                                 */
                                                /* L : 리보금리                                 */
                                                /* B : 주요국정부채                             */
    char    symb[10];                           /* 심볼                                         */
    char    hts_eng_isnm[39];                   /* 영문명                                       */
    char    hts_kor_isnm[40];                   /* 한글명                                       */
    char    bstp_cls_code[4];                   /* 종목업종코드                                 */
    char    dow_30_yn[1];                       /* 다우30 편입종목여부    0:미편입 1:편입       */
    char    nasdaq_100_yn[1];                   /* 나스닥100 편입종목여부 0:미편입 1:편입       */
    char    snp_500_yn[1];                      /* S&P 500  편입종목여부  0:미편입 1:편입       */
    char    exch_cls_code[4];                   /* 거래소코드                                   */
    char    ntnl_cls_code[3];                   /* 국가구분코드                                 */
} ST_FRGN_CODE;
