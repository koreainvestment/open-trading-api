/*****************************************************************************
 *  해외 선물 파일 구조 (ffcode.mst)
 ****************************************************************************/
typedef struct ST_FFCODE_TBL
{
	char sSrsCd [ 32]; /* 종목코드 */
	char sAutoOrdGnrlYN[ 1]; /* 서버자동주문 가능 종목 여부 */
	char sAutoOrdTwapYN[ 1]; /* 서버자동주문 TWAP 가능 종목 여부 */
	char sAutoOrdEcnmYN[ 1]; /* 서버자동 경제지표 주문 가능 종목 여부 */
	char sFiller [ 47]; /* 필러 */
	char sSeriesKrNm [ 50]; /* 종목한글명 */
	char sExchCd [ 10]; /* 거래소코드 (ISAM KEY 1) */
	char sMrktCd [ 10]; /* 품목코드 (ISAM KEY 2) */
	char sClasCd [ 3]; /* 품목종류 */
	char sDispDesz [ 5]; /* 출력 소수점 */
	char sCalcDesz [ 5]; /* 계산 소수점 */
	char sTickSz [ 14]; /* 틱사이즈 */
	char sTickVal [ 14]; /* 틱가치 */
	char sCtrtSz [ 10]; /* 계약크기 */
	char sDispDigit [ 4]; /* 가격표시진법 */
	char sMultiplier [ 10]; /* 환산승수 */
	char sNearFlg [ 1]; /* 최다월물여부 0:원월물 1:최다월물 */
	char sNearFlgDt [ 1]; /* 최근월물여부 0:원월물 1:최근월물 */
	char sSprdYN [ 1]; /* 스프레드여부 */
	char sSprdLeg1YN [ 1]; /* 스프레드기준종목 LEG1 여부 Y/N */
	char sExchSubCd [ 2]; /* 서브 거래소 코드 */
} FFCODE_TBL;
